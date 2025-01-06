from enum import Enum
import sqlite3
import os
import re
import sys
import struct

import dataset

class ParseState(Enum):
    HEADER = 0,
    VERSION = 1
    AIDA_CPUID = 2
    MOTHERBOARD = 3
    CPUID = 4
    MSRS = 5
    REMAINDER = 6
    CPU_SUMMARY = 7
    DONE = 8

class ParsedFeature:
    def __init__(self, shortname, longname, value, present=True):
        self.shortname = shortname
        self.longname = longname
        self.value = value
        self.present = present

    def value(self):
        if self.present:
            return self.value
        else:
            return None

    def show(self):
        return "{}: {}".format(self.shortname, self.value)

    def __str__(self):
        if self.value:
            return self.show()
        else:
            return "-{}".format(self.shortname)

class CPUIDFeature:
    def __init__(self, shortname, longname, leaf, reg, offset, width,
            subleaf=None, filter=None):
        self.shortname = shortname
        self.longname = longname
        self.reg = reg
        self.offset = offset
        self.width = width
        self.leaf = leaf
        self.subleaf = subleaf
        self.filter = filter
        self.value = None

    def parse(self, info, db):
        if self.filter and not self.filter(info):
            # TODO: parse a value anyway, just to see if it was non-zero
            return None

        # TODO: assume all CPUs report the same cpuid .... for now
        if self.leaf not in info.cpuid[0]:
            # TOOD: no self.value means we parsed nothing. this probably be a
            # bit more explicit..
            return self.into_non_present()

        top_level = info.cpuid[0][self.leaf]
        leaf = None
        if self.subleaf is not None:
            if self.subleaf in top_level:
                leaf = top_level[self.subleaf]
            else:
                return None
        else:
            leaf = top_level

        if self.reg not in leaf:
            if not isinstance(leaf, dict):
                raise Exception("""{} does not describe a subleaf, but leaf \
                    {:x} has subleaves?""".format(self.shortname, self.leaf))

        reg = leaf[self.reg]

        bits = (reg >> self.offset) & ((1 << self.width) - 1)

        return self.into_present(bits)

    def present(self):
        raise Exception("What")

    def into_non_present(self):
        return ParsedFeature(
            self.shortname,
            self.longname,
            None,
            present=False
        )

    def into_present(self, value):
        return ParsedFeature(
            self.shortname,
            self.longname,
            value,
        )

class CPUIDFCMOV(CPUIDFeature):
    def __init__(self):
        super().__init__("FCMOV", "x87 CMOVcc", None, None, None, 2, None)

    def present(self):
        return self.value == 1

    def parse(self, info, db):
        leaf = info.cpuid[0][0x00000001]

        edx = leaf['edx']

        present = edx & 0x00008001 == 0x00008001

        if present:
            self.value = 1
        else:
            self.value = 0

class CPUIDBoolFeature(CPUIDFeature):
    def __init__(self, shortname, longname, leaf, reg, offset, subleaf=None):
        super().__init__(shortname, longname, leaf, reg, offset, 1, subleaf)

    def present(self):
        return self.value == 1

    def show(self):
        if self.value == 1:
            return self.shortname

AMD_CPU_PRODUCT_INFO = {
    "Am5x86": {
        "datasheet": "https://datasheets.chipdb.org/AMD/486_5x86/19751C.pdf",
        "date": {
            "after": "01/03/1996",
            "after_ref": "datasheet",
            "before": "01/12/1996",
            "before_ref": "citations no https://en.wikipedia.org/wiki/Am5x86"
        }
    }
}

class CPUIDVendor:
    def __init__(self):
        self.shortname = "vendor"
        self.longname = "CPUID-defined vendor string from leaf 0h"

    def parse(self, info, db):
        if 0x00000000 not in info.cpuid[0]:
            return None

        brand = info.cpuid[0][0x00000000]

        # yes it's in b, d, c order.
        vendorname = struct.pack("<III", brand['ebx'], brand['edx'],
                brand['ecx'])

        info.add_feature(ParsedFeature(
            self.shortname, self.longname, vendorname.decode("utf8")
        ))

class CPUIDUarch:
    def __init__(self):
        self.shortname = "uarch"
        self.longname = """Microarchitecture of the processor as informed by \
            Family/Model/Stepping fields"""

    def parse(self, info, db):
        if 0x00000000 not in info.cpuid[0]:
            return None

        brand = info.cpuid[0][0x00000000]

        vendorname = info.feature("vendor").value

        uarch = None

        if vendorname == "AuthenticAMD":
            uarch = self.parse_amd(info, db)
        elif vendorname == "GenuineIntel":
            uarch = self.parse_intel(info, db)
#        else:
#            print("""cannot currently handle processors from vendor \
#                    {}""".format(vendorname))

        if uarch is None:
            return

        info.add_feature(ParsedFeature(
            "uarch", "CPUID-implied processor architecture",
            uarch
        ))

        info.add_feature(ParsedFeature(
            "family", "CPUID-implied processor family",
            db['uarches'].find_one(id=uarch)['family']
        ))


    def parse_intel(self, info, db):
        family = info.feature("FamilyID").value
        ext_family = info.feature("ExtendedFamilyID").value

        model = info.feature("ModelID").value
        ext_model = info.feature("ExtendedModelID").value

        fm = db.query("""\
            select uarch from family_model_info join vendors on
            family_model_info.vendor = vendors.id \
            where \
                vendors.name="Intel" and \
                family_model_info.family={} and \
                family_model_info.ext_family={} and \
                family_model_info.model={} and \
                family_model_info.ext_model={}""".format(
            family, ext_family, model, ext_model))

        try:
            fm = fm.next()
            fm = fm['uarch']
        except:
            print("unknown family and/or model: {:x}h+{:x}h/{:x}h+{:x}".format(
                family, ext_family,
                model, ext_model))
            print("  {}".format(info.cpuid_name))

    def parse_amd(self, info, db):
        family = info.feature("FamilyID").value
        ext_family = info.feature("ExtendedFamilyID").value

        model = info.feature("ModelID").value
        ext_model = info.feature("ExtendedModelID").value

        fm = db.query("""\
            select uarch from family_model_info join vendors on
            family_model_info.vendor = vendors.id \
            where \
                vendors.name="AMD" and \
                family_model_info.family={} and \
                family_model_info.ext_family={} and \
                family_model_info.model={} and \
                family_model_info.ext_model={}""".format(
            family, ext_family, model, ext_model))

        try:
            fm = fm.next()
            fm = fm['uarch']
            return fm
        except:
            print("unknown family and/or model: {:x}h+{:x}h/{:x}h+{:x}".format(
                family, ext_family,
                model, ext_model))
            print("  {}".format(info.cpuid_name))

ISA_EXTENSIONS = [
    # the following are from the AMD Architecture Programmer's Manual Volume 3,
    # table D2. Document 24594 Rev 3.36 (March 2024).
    CPUIDBoolFeature("3DNow", "3DNow!", 0x80000001, "edx", 31),
    CPUIDBoolFeature("3DNowExt", "3DNow! Extensions", 0x80000001, "edx", 30),
    CPUIDBoolFeature("3DNowPrefetch", """Prefetch instructions from 3DNow!, \
    PREFETCH and PREFETCHW""", 0x80000001, "ecx", 8),
    CPUIDBoolFeature("3DNowPrefetch", """Prefetch instructions from 3DNow!, \
    PREFETCH and PREFETCHW""", 0x80000001, "edx", 29),
    CPUIDBoolFeature("3DNowPrefetch", """Prefetch instructions from 3DNow!, \
    PREFETCH and PREFETCHW""", 0x80000001, "edx", 31),
    # so the story i gather is, AMD introduced ABM, but somehow presence of the
    # ABM instructions was moved to be indicated by the BMI1 bit, and the ABM
    # bit just indicates (for both Intel and AMD) if LZCNT is not BSR...?
    #
    # HELP! if true this means some processor indicates more than just LZCNT
    # with this bit..
    CPUIDBoolFeature("ABM", "Advanced Bit Manipulation (just LZCNT though)",
        0x80000001, "ecx", 5),
    # distinct from CLFSH?? and the APM also reports this at eax=7 ecx=0 bit 24
    # like SDM..
    CPUIDBoolFeature("CLWB", "CLWB", 0x80000008, "ebx", 0),
    CPUIDBoolFeature("F16C", "16-bit floating-point conversion", 0x00000001,
        "ecx", 29),
    CPUIDBoolFeature("FMA4", "FMA4", 0x80000001, "ecx", 16),
    CPUIDBoolFeature("FPU", "x87", 0x80000001, "edx", 0),
    CPUIDBoolFeature("INVLPGB", "INVLPGB/TLBSYNC", 0x80000008, "ebx", 3),
    CPUIDBoolFeature("LahfSahf", "LAHF/SAHF", 0x80000001, "ecx", 0),
    CPUIDBoolFeature("LM", "Long Mode (AMD64)", 0x80000001, "edx", 29),
    CPUIDBoolFeature("MCOMMIT", "MCOMMIT", 0x80000008, "ebx", 8),
    CPUIDBoolFeature("MmxExt", "MMX Extensions", 0x80000001, "edx", 22),
    CPUIDBoolFeature("MONITORX", "MONITORX/MWAITX", 0x80000001, "ecx", 29),
    CPUIDBoolFeature("RDPRU", "RDPRU", 0x80000008, "ebx", 4),
    CPUIDBoolFeature("RDTSCP", "RDTSCP", 0x80000001, "edx", 27),
    CPUIDBoolFeature("SevEs", "VMGEXIT", 0x8000001f, "eax", 3),
    CPUIDBoolFeature("SKINIT", "SKINIT/STGI", 0x80000001, "ecx", 12),
    CPUIDBoolFeature("SMAP", "CLAC/STAC", 0x00000017, "ebx", 20),
    CPUIDBoolFeature("SNP (4)", """PSMASH/PVALIDATE/RMPADJUST/RMPUPDATE""",
        0x8000001f, "eax", 4),
    CPUIDBoolFeature("SNP (6)", "RMPQUERY", 0x8000001f, "eax", 6),
    CPUIDBoolFeature("SNP (21)", "RMPREAD", 0x8000001f, "eax", 21),
    CPUIDBoolFeature("SSE4A", "SSE4A", 0x80000001, "ecx", 6),
    CPUIDBoolFeature("SVM", "Secure Virtual Machine", 0x80000001, "ecx", 2),
    CPUIDBoolFeature("SysCallSysRet", "SYSCALL/SYSRET", 0x80000001, "edx", 11),
    CPUIDBoolFeature("TBM", "Trailing bit manipulation", 0x80000001, "ecx", 21),
    # needs two different bits set, so special parsing logic..
    CPUIDFCMOV(),
    CPUIDBoolFeature("XOP", "XOP", 0x80000001, "ecx", 11),
    CPUIDBoolFeature("XSAVEC", "XSAVEC", 0x0000000d, "eax", 1, subleaf=1),
    CPUIDBoolFeature("XSAVEOPT", "XSAVEOPT", 0x0000000d, "eax", 0, subleaf=1),
    CPUIDBoolFeature("XSAVES/XRSTORS", "XSAVES/XRSTORS", 0x0000000d, "eax", 3,
        subleaf=1),

    # the following come from the Intel SDM. there, extensions are included in
    # "Table 3-17. Information Returned by CPUID Instruction", under
    # documentation for the CPUID instruction. documentation for leaf 1 feature
    # bits are in later figures as well..
    # HELP! which instructions does this relate to?
    CPUIDBoolFeature("VMX", "processor supports Virtual Machine Extensions",
        0x00000001, "ecx", 5),
    # HELP! which instructions does this relate to?
    CPUIDBoolFeature("SMX", "processor supports Safer Mode Extensions",
        0x00000001, "ecx", 6),

    CPUIDBoolFeature("MPX", "Memory Protection Extensions", 0x00000007,
        "ebx", 14, subleaf=0),
    CPUIDBoolFeature("AVX512F", "AVX512F", 0x00000007,
        "ebx", 16, subleaf=0),
    CPUIDBoolFeature("AVX512DQ", "AVX512DQ", 0x00000007,
        "ebx", 17, subleaf=0),
    CPUIDBoolFeature("AVX512_IFMA", "AVX512_IFMA", 0x00000007,
        "ebx", 21, subleaf=0),
    CPUIDBoolFeature("AVX512PF", "AVX512PF", 0x00000007,
        "ebx", 26, subleaf=0),
    CPUIDBoolFeature("AVX512ER", "AVX512ER", 0x00000007,
        "ebx", 27, subleaf=0),
    CPUIDBoolFeature("AVX512CD", "AVX512CD", 0x00000007,
        "ebx", 28, subleaf=0),
    CPUIDBoolFeature("AVX512BW", "AVX512BW", 0x00000007,
        "ebx", 30, subleaf=0),
    CPUIDBoolFeature("AVX512VL", "AVX512VL", 0x00000007,
        "ebx", 31, subleaf=0),

    CPUIDBoolFeature("PREFETCHWT1", "PREFETCHWT1", 0x00000007,
        "ecx", 0, subleaf=0),
    CPUIDBoolFeature("AVX512_VBMI", "AVX512_VBMI", 0x00000007,
        "ecx", 1, subleaf=0),
    CPUIDBoolFeature("WAITPKG", "umonitor/umwait support", 0x00000007,
        "ecx", 5, subleaf=0),
    CPUIDBoolFeature("AX512_VBMI2", "AVX512_VBMI2", 0x00000007,
        "ecx", 6, subleaf=0),
    CPUIDBoolFeature("GFNI", "GFNI", 0x00000007,
        "ecx", 8, subleaf=0),
    CPUIDBoolFeature("AVX512_VNNI", "AVX512_VNNI", 0x00000007,
        "ecx", 11, subleaf=0),
    CPUIDBoolFeature("AVX512_BITALG", "AVX512_BITALG", 0x00000007,
        "ecx", 12, subleaf=0),
    CPUIDBoolFeature("AVX512_VPOPCNTDQ", "AVX512_VPOPCNTDQ", 0x00000007,
        "ecx", 14, subleaf=0),
    CPUIDBoolFeature("KL", "Key Locker support", 0x00000007,
        "ecx", 23, subleaf=0),
    CPUIDBoolFeature("CLDEMOTE", "Cache line demote support", 0x00000007,
        "ecx", 25, subleaf=0),
    CPUIDBoolFeature("MOVDIRI", "MOVDIRI supported", 0x00000007,
        "ecx", 27, subleaf=0),
    CPUIDBoolFeature("MOVDIR64B", "MOVDIR64B supported", 0x00000007,
        "ecx", 28, subleaf=0),
    CPUIDBoolFeature("ENQCMD", "Enqueue Stores support (ENQCMD instruction)",
        0x00000007, "ecx", 28, subleaf=0),

    CPUIDBoolFeature("AVX512_4VNNIW", "AVX512_4VNNIW",
        0x00000007, "edx", 2, subleaf=0),
    CPUIDBoolFeature("AVX512_4FMAPS", "AVX512_4FMAPS",
        0x00000007, "edx", 3, subleaf=0),
    CPUIDBoolFeature("AVX512_VP2INTERSECT", "AVX512_VP2INTERSECT",
        0x00000007, "edx", 8, subleaf=0),
    CPUIDBoolFeature("SERIALIZE", "serialize instruction supported",
        0x00000007, "edx", 14, subleaf=0),
    CPUIDBoolFeature("PCONFIG", "PCONFIG instruction supported",
        0x00000007, "edx", 18, subleaf=0),
    CPUIDBoolFeature("AMX-BF16", "AMX operations supported on bfloat 16",
        0x00000007, "edx", 22, subleaf=0),
    CPUIDBoolFeature("AVX512_FP16", "AVX512_FP16",
        0x00000007, "edx", 23, subleaf=0),
    CPUIDBoolFeature("AMX-TILE", "AMX operations supports tile architecture",
        0x00000007, "edx", 24, subleaf=0),
    CPUIDBoolFeature("AMX-INT8", "AMX operations supported on 8-bit integers",
        0x00000007, "edx", 25, subleaf=0),

    CPUIDBoolFeature("AVX-VNNI", "AVX-VNNI",
        0x00000007, "eax", 4, subleaf=1),
    CPUIDBoolFeature("AVX512_BF16", "AVX512_BF16",
        0x00000007, "eax", 5, subleaf=1),
    CPUIDBoolFeature("HRESET", "HRESET instruction support",
        0x00000007, "eax", 22, subleaf=1),

    # the following have the same definitions in both Intel SDM and AMD APM.
    # they are generally ordered in Intel's order because i wrote feature
    # definitions for AMD first, then hoisted as i saw matching definitions in
    # the SDM.
    CPUIDBoolFeature("SSE3", "SSE3", 0x00000001, "ecx", 0),
    CPUIDBoolFeature("PCLMULDQ", "PCLMULDQ", 0x00000001, "ecx", 1),
    CPUIDBoolFeature("monitor", "monitor/mwait instructions", 0x00000001,
        "ecx", 3),
    CPUIDBoolFeature("SSSE3", "SSSE3", 0x00000001, "ecx", 9),
    CPUIDBoolFeature("FMA", "FMA", 0x00000001, "ecx", 12),
    CPUIDBoolFeature("CMPXCHG16B", "CMPXCHG16B", 0x00000001, "ecx", 13),
    CPUIDBoolFeature("SSE41", "SSE4.1", 0x00000001, "ecx", 19),
    CPUIDBoolFeature("SSE42", "SSE4.2", 0x00000001, "ecx", 20),
    CPUIDBoolFeature("MOVBE", "MOVBE", 0x00000001, "ecx", 22),
    CPUIDBoolFeature("POPCNT", "POPCNT", 0x00000001, "ecx", 23),
    CPUIDBoolFeature("AES", "AESNI?", 0x00000001, "ecx", 25),
    CPUIDBoolFeature("XSAVE", "XSAVE/XRSTOR", 0x00000001, "ecx", 26),
    CPUIDBoolFeature("AVX", "Advanced Vector Extensions", 0x00000001, "ecx", 28),
    CPUIDBoolFeature("F16C", "floating-point 16-bit conversions", 0x00000001,
        "ecx", 29),
    CPUIDBoolFeature("RDRAND", "RDRAND", 0x00000001, "ecx", 30),

    CPUIDBoolFeature("TSC", "RDTSC", 0x00000001, "edx", 4),
    CPUIDBoolFeature("MSR", "RDMSR/WRMSR", 0x00000001, "edx", 5),
    CPUIDBoolFeature("CMPXCHG8B", "CMPXCHG8B", 0x00000001, "edx", 8),
    CPUIDBoolFeature("SysEnterSysRet", """sysenter/sysret instructions. Intel \
        calls these "sysenter" and "sysexit". this bit also indicates \
        related MSRs (HELP! WHICH?) are present.""", 0x00000001, "edx", 11),
    CPUIDBoolFeature("CMOV", "CMOVcc", 0x00000001, "edx", 15),
    CPUIDBoolFeature("CLFSH", "CLFLUSH/CLWB", 0x00000001, "edx", 19),
    CPUIDBoolFeature("MMX", "MMX", 0x00000001, "edx", 23),
    CPUIDBoolFeature("FXSR", "FXSAVE/FXRSTOR", 0x00000001, "edx", 24),
    CPUIDBoolFeature("SSE", "SSE1", 0x00000001, "edx", 25),
    CPUIDBoolFeature("SSE2", "SSE2", 0x00000001, "edx", 26),

    CPUIDBoolFeature("FSGSBASE", """instruction for FS/GS base read/write \
        (instead of RDMSR/WRMSR)""", 0x00000007, "ebx", 0, subleaf=0),
    CPUIDBoolFeature("BMI1", "Bit manipulation group 1 instructions",
        0x00000007, "ebx", 3, subleaf=0),
    CPUIDBoolFeature("AVX2", "Advanced Vector Extensions 2", 0x00000007,
        "ebx", 5, subleaf=0),
    CPUIDBoolFeature("BMI2", "Bit Manipulation, group 2", 0x00000007,
        "ebx", 8, subleaf=0),
    CPUIDBoolFeature("INVPCID", "INVPCID", 0x00000007, "ebx", 10, subleaf=0),
    CPUIDBoolFeature("RDSEED", "RDSEED", 0x00000007, "ebx", 18, subleaf=1),
    CPUIDBoolFeature("ADX", "ADCX/ADOX", 0x00000007, "ebx", 19, subleaf=0),
    CPUIDBoolFeature("CLFLOPT", "CLFLUSHOPT", 0x00000007, "ebx", 23, subleaf=0),
    CPUIDBoolFeature("SHA", "SHA", 0x00000007, "ebx", 29, subleaf=0),

    CPUIDBoolFeature("OSPKE", "RDPKRU/WRPKRU", 0x00000007, "ecx", 4, subleaf=0),
    CPUIDBoolFeature("CET_SS", """Control-flow Enforcement Technology - Shadow \
        Stack""", 0x00000007, "ecx", 7, subleaf=0),
    CPUIDBoolFeature("VAES", "VAES 256-bit instructions", 0x00000007, "ecx", 9,
        subleaf=0),
    CPUIDBoolFeature("VPCLMULQDQ", "VPCLMULQDQ 256-bit instructions",
        0x00000007, "ecx", 10, subleaf=0),
    CPUIDBoolFeature("RDPID", "RDPID", 0x00000007, "ecx", 22, subleaf=0),
]

# more features from the SDM, table 3-17.
# HELP! i've skipped a lot of bits here.
INTEL_FEATURES = [
    CPUIDBoolFeature("EIST", """processor supports Enhanced Intel SpeedStep \
        Technology""", 0x00000001, "ecx", 7),
    CPUIDBoolFeature("TM2", "Thermal Monitor 2", 0x00000001, "ecx", 8),

    CPUIDFeature("monitor-min", "minimum size of a MONITOR line in bytes",
        0x00000005, "eax", 0, 16),
    CPUIDFeature("monitor-max", "maximum size of a MONITOR line in bytes",
        0x00000005, "ebx", 0, 16),
    CPUIDFeature("mwait-break-on-int", """mwait can be set to break on \
        interrupt even when interrupts are disabled""", 0x00000005, "ebx", \
        0, 16),
    CPUIDFeature("C0 substates", """Number of supported C0 sub-states \
        supported by MWAIT""", 0x00000005, "edx", 0, 4),
    CPUIDFeature("C1 substates", """Number of supported C1 sub-states \
        supported by MWAIT""", 0x00000005, "edx", 4, 4),
    CPUIDFeature("C2 substates", """Number of supported C2 sub-states \
        supported by MWAIT""", 0x00000005, "edx", 8, 4),
    CPUIDFeature("C3 substates", """Number of supported C3 sub-states \
        supported by MWAIT""", 0x00000005, "edx", 12, 4),
    CPUIDFeature("C4 substates", """Number of supported C4 sub-states \
        supported by MWAIT""", 0x00000005, "edx", 16, 4),
    CPUIDFeature("C5 substates", """Number of supported C5 sub-states \
        supported by MWAIT""", 0x00000005, "edx", 20, 4),
    CPUIDFeature("C6 substates", """Number of supported C6 sub-states \
        supported by MWAIT""", 0x00000005, "edx", 24, 4),
    CPUIDFeature("C7 substates", """Number of supported C7 sub-states \
        supported by MWAIT""", 0x00000005, "edx", 28, 4),

    CPUIDBoolFeature("PLN", "Power limit notification support", 0x00000006,
        "eax", 4),
    CPUIDBoolFeature("ECMD", "Clock modulation duty cycle support", 0x00000006,
        "eax", 5),
    CPUIDBoolFeature("PTM", "Package thermal management support", 0x00000006,
        "eax", 6),
    CPUIDBoolFeature("turbo-boost-3", "Intel Turbo Boost Max Technology 3.0",
        0x00000006, "eax", 14),

    CPUIDBoolFeature("hardware-coordination-feedback",
        "APERF/MPERF MSRs present", 0x00000006, "ecx", 0),

    CPUIDFeature("TSC:CLK (denominator)", "", 0x00000015, "eax", 0, 32),
    CPUIDFeature("TSC:CLK (numerator)", "", 0x00000015, "ebx", 0, 32),
    CPUIDFeature("base CCLK", "", 0x00000016, "eax", 0, 16),
    CPUIDFeature("max CCLK", "", 0x00000016, "ebx", 0, 16),
]



FEATURES = [
    CPUIDBoolFeature("TscInvariant", """TSC runs at a constant frequency in all \
            P- and C-states""", 0x80000007, "edx", 8),
    CPUIDBoolFeature("ARAT", "Always Running APIC Timer", 0x00000006, "eax", 2),
    CPUIDFeature("ExtendedFamilyID", "Extended Family ID", 0x00000001, "eax", 20,
        4),
    CPUIDFeature("ExtendedModelID", "Extended Model ID", 0x00000001, "eax", 16,
        4),
    CPUIDFeature("FamilyID", "Family ID", 0x00000001, "eax", 8, 4),
    CPUIDFeature("ModelID", "Model ID", 0x00000001, "eax", 4, 4),

    CPUIDBoolFeature("Virtualized", "Running on a virtual processor",
        0x00000001, "ecx", 31),
    CPUIDFeature("Hypervisor leaves", "Microsoft Hypervisor CPUID leaves",
        0x40000000,"eax", 0, 32),

    CPUIDBoolFeature("DecodeAssist", "SVM helps decode instructions on VMEXIT",
        0x8000000A,"edx", 7),
    CPUIDBoolFeature("AVIC", "SVM has AVIC support",
        0x8000000A,"edx", 13),
    CPUIDBoolFeature("x2AVIC", "SVM has x2AVIC support",
        0x8000000A,"edx", 18),

    CPUIDVendor(),
    CPUIDUarch(),

    CPUIDBoolFeature("XGETBV w/ ECX=1", "XGETBV /w ECX=1", 0x0000000d,
        "eax", 2, subleaf=1)
]

FEATURES += ISA_EXTENSIONS

section_headers = {
        "------[ Versions ]------": ("versions", ParseState.VERSION),
        "------[ CPU Info ]------": ("aida_cpuid", ParseState.AIDA_CPUID),
        "------[ Motherboard Info ]------": ("motherboard_info", ParseState.MOTHERBOARD),
        "------\[ CPUID Registers / Logical CPU #(\d+) \]------": ("cpuid", ParseState.CPUID),
        "CPUID Registers \(CPU #(\d+)\)": ("cpuid", ParseState.CPUID),
        # for some files, SMT twins are indicated by a slightly different header
        # string...
        "CPUID Registers \(CPU #(\d+) Virtual\)": ("cpuid", ParseState.CPUID),
        "CPU#(\d+) AffMask.*": ("cpuid", ParseState.CPUID),
        "------\[ Logical CPU #(\d+) \]------": ("cpuid", ParseState.CPUID),
        # `AuthenticAMD0A70F80_K19_Phoenix2_01_CPUID.txt` has atypical leaders
        # on cpuid regions, which include an indicator of cpu number but not
        # really an explicit statement. we'll do some fixup on these...
        "Group: 0x00 Affinity mask: 0x[0-9A-F]+": ("cpuid", ParseState.CPUID),
        "------[ All CPUs ]------": ("cpus_summary", ParseState.DONE),
        "------\[ MSR Registers / Logical CPU #([0-9]+) \]------": ("msrs", ParseState.MSRS),
        "------[ MSR Registers ]------": ("msrs", ParseState.MSRS),
        "MSR Registers \(CPU #(\d+)\)": ("msrs", ParseState.MSRS),
        # `AuthenticAMD0040F12_K8_SantaRosa_CPUID_S8.txt` only has one MSR block
        # to go with the 16 CPUs..
        "MSR Registers": ("msrs", ParseState.MSRS),
        "PerformanceFrequency =.*": ("remainder", ParseState.REMAINDER)
}

version_lines = {
    "Program Version :": "aida",
    "LLKD Version    :": "llkd",
    "BenchDLL Version:": "benchdll",
    "Windows Version :": "windows",
    "GetProductInfo  :": "getproductinfo"
}

aida_cpu_lines = {
    "CPU Type          :": "synth_type",
    "CPU Alias         :": "alias",
    "CPU Platform      :": "platform",
    "CPU Stepping      :": "stepping",
    "Instruction Set   :": "exts",
    "CPUID Manufacturer:": "cpuid_manufacturer",
    "CPUID CPU Name    :": "cpuid_type",
    "CPUID Revision    :": "cpuid_revision",
    "Platform ID       :": "platform",
    "HTT / CMP Units   :": "http_cmp",
    "Max. NUMA Node    :": "max_numa",
    "Max. NUMA Node     :": "max_numa",
    "Tjmax Temperature       :": "tjmax",
    "HTC Temperature Limit   :": "htc_lim",
    "CPU Thermal Design Power:": "tdp",

    # older AIDA versions format a bit differently...
    "CPU Type           :": "synth_type",
    "CPU Alias          :": "alias",
    "CPU Platform       :": "platform",
    "CPU Stepping       :": "stepping",
    "Instruction Set    :": "exts",
    "CPUID Manufacturer :": "cpuid_manufacturer",
    "CPUID CPU Name     :": "cpuid_type",
    "CPUID Revision     :": "cpuid_revision",
    "AMD Old Brand ID   :": "old_brand_id",
    "AMD New Brand ID   :": "new_brand_id",
    "AMD K10 Brand ID   :": "k10_brand_id",
    "AMD K1x Brand ID   :": "k1x_brand_id",
    "IA Brand ID        :": "ia_brand_id",
    "IA Brand ID       :": "ia_brand_id",
    "Platform ID        :": "platform",
    "HTT / CMP Units    :": "http_cmp",
    "Tjmax Temperature              :": "tjmax",
    "Tjmax Temperature          :": "tjmax",
    "Tjmax Temperature        :": "tjmax",
    "Tjmax Temperature    :": "tjmax",
    "Tjmax Temperature  :": "tjmax",
    "HTC Temperature Limit          :": "htc_lim",
    "HTC Temperature Limit      :": "htc_lim",
    "HTC Temperature Limit    :": "htc_lim",
    "HTC Temperature Limit:": "htc_lim",
    "CPU TDP              :": "tdp",
    "CPU TDP                  :": "tdp",
    "CPU TDP                    :": "tdp",
    "CPU TDP                        :": "tdp",
    "CPU TDC                    :": "tdc",
    "CPU TDC                  :": "tdc",
    "CPU TDC               :": "tdc",
    "CPU TDC              :": "tdc",
    "DRAM TDP                   :": "dram_tdp",
    "CPU Max Power Limit        :": "max_power_lim",
    "CPU Max Power Limit      :": "max_power_lim",
    "CPU Max Power Limit  :": "max_power_lim",
    "CPU Power Limit 1 (Long)   :": "cpu_power_lim_1",
    "CPU Power Limit 1 (Long) :": "cpu_power_lim_1",
    "CPU Power Limit 2 (Short)  :": "cpu_power_lim_2",
    "CPU Power Limit 2 (Short):": "cpu_power_lim_2",
    "Max Turbo Boost Multipliers:": "turbo_mult_schedule",
    "Socket / Min / Max / Target TDP:": "tdp_info"
}

motherboard_lines = {
    "Motherboard ID      :": "id",
    "Motherboard Model   :": "model",
    "Motherboard Chipset :": "chipset",

    "Award BIOS Type     :": "bios_type",
    "Award BIOS Message  :": "bios_message",

    "DMI MB Manufacturer :": "manufacturer",
    "DMI MB Product      :": "product",
    "DMI MB Version      :": "version",
    "DMI MB Serial       :": "serial",
    "DMI SYS Manufacturer:": "sys_manufacturer",
    "DMI SYS Product     :": "sys_product",
    "DMI SYS Version     :": "sys_version",
    "DMI SYS Serial      :": "sys_serial",
    "DMI BIOS Version    :": "bios_version",
}

class AIDAInfo:
    def feature(self, name):
        for feat in self.parsed_features:
            if feat.shortname == name:
                return feat

        return None

    def add_feature(self, feat_info):
        self.parsed_features.append(feat_info)

    def proc_name(self):
        family = self.feature("FamilyID").value
        ext_family = self.feature("ExtendedFamilyID").value
        if ext_family:
            family += ext_family

        model = self.feature("ModelID").value
        ext_model = self.feature("ExtendedModelID").value
        if ext_model:
            model += ext_model

        # especially for older processors, a brand string might be present but
        # it might be insufficiently distinct to cohabitate with other
        # processors from the same family - there were several models of K5
        # processor, but their brand strings are all "AMD-K5(tm) Processor", for
        # example. so, if we know the brand string isn't distinctive enough,
        # list it here and append family/model. at that point, if it's still not
        # unique, it might actually be a duplicate cpuid measurement.
        needs_disambiguation = [
            "AMD-K5(tm) Processor",
            "AMD-K6tm w/ multimedia extensions",
            "AMD-K6(tm) 3D processor",
            "AMD-K6(tm)-III Processor",
            "AMD Athlon(tm) Processor",
            "AMD Duron(tm) processor",
            "AMD Engineering Sample"
        ]

        if self.cpuid_name:
            if self.cpuid_name in needs_disambiguation:
                return "{} family {:x}h/model {:x}h".format(
                    self.cpuid_name, family, model
                )
            else:
                return self.cpuid_name
        else:
            return "Unknown {} family {:x}h model {:x}h".format(
                self.feature("vendor"),
                family,
                model
            )

    # some processors in The Great CPUID Collection are actually measured from
    # inside a VM. for many bits this is fine - ISA extensions are typically
    # passed through, CPU/cache topology should still be accurate. but some bits
    # and features, especially ones that do not make sense to a guest VM, like
    # SVM capabilities or APIC management, may be incomplete, incorrect, or
    # reflect virtualized hardware rather than a configuration of a physical
    # processor.
    #
    # so, check a few ways we might spot a vitual processor reaading so we can
    # set it aside.
    def suspected_virtual(self):
        feat = self.feature("Virtual")
        if feat and feat.present and feat.value == 1:
            return True
        feat = self.feature("Hypervisor leaves")
        if feat and feat.present and feat.value > 0:
            return True

        return False

    def __init__(self, db, text):
        global FEATURES
        state = ParseState.HEADER
        self.name = None
        self.version = {}
        self.aida_cpuid = {}
        self.motherboard = {}
        self.cpuid = {}
        self.parsed_features = []

        # some CPUID files have no headers before cpuid blocks at all.
        # so we'll just have to guess the current CPU number based on how many
        # times we've seen `CPUID 00000000`?
        # see `GenuineIntel0090675_AlderLake_01_CPUID.txt`
        self.guessed_cpu_nr = 0
        self.guessing_cpu_nr = False

        # some CPUID files have no suffix indicating which subleaf a query
        # refers to. so, guess that subsequent rows for a leaf mean that it's
        # actually a series of subleaves.
        self.guessed_cpuid_subleaf_nr = 0
        self.guessing_cpuid_subleaf_nr = None

        # TODO: header checks below should really be their own function, and
        # files should be presumed headerless until shown otherwise - if header
        # checks were extracted out this would be an easy check when it returns.
        # but instaed this is one big mash of control flow.
        self.headerless = False

        # didn't have enough to correctly identify core/thread numbers when
        # walking cpuid readings. core numbers may be wrong!
        self.inaccurate_core_number = False

        # `GenuineIntel00006F2_Conroe_CPUID.txt`. it's
        # the only one. (i think.)
        #
        # the CPU numbers in that file just start from 1.
        self.cpus_start_counting_from_1 = False

        # some files (GenuineIntel0090661_ElkhartLake_02_CPUID.txt) start with
        # an empty line. so instead of checking for linenr==0 below to determine
        # appropriate parsing hacks, use this and set it appropriately when a
        # real line of data is seen.
        self.first_data_line = None

        for (linenr, line) in enumerate(text):

            if state == ParseState.DONE:
                break

            line = line.strip()

            if line == "":
                continue
            elif self.first_data_line == None:
                self.first_data_line = True
            else:
                self.first_data_line = False

            # some files have no header and open directly into CPUID info.
            # ... some of these are clearly many-cpu parts
            # (GenuineIntel0050670_KnightsLanding_CPUID.txt for example), so i'm
            # not sure how much i trust their data...
            if line.startswith("CPUID 00000000"):
                if self.first_data_line:
                    self.headerless = True
                    self.guessing_cpu_nr = True
                    self.guessed_cpu_nr = 0
                elif self.headerless:
                    if not self.guessing_cpu_nr:
                        raise Exception("""duplicate CPUID 00000000 in \
                            {}?""".format(sys.argv[1]))
                    self.guessed_cpu_nr += 1

                if self.headerless:
                    state = ParseState.CPUID

                    self.cpuid[self.guessed_cpu_nr] = {}
                    cpuid_buf = self.cpuid[self.guessed_cpu_nr]
                    cpuid_buf["location"] = {
                        "package": int(0),
                        "core": int(self.guessed_cpu_nr),
                        "thread": int(0)
                    }

            parsed = False

            # if we're in any of the known regions, read the line as some data
            # declaration for that kind of information.  if the line is unknown,
            # it might be the header for a new region, so reset state
            # to HEADER.

            # finally, if we've tried and failed to handle the line, or we know
            # ahead of time we're looking for a new HEADER line, try matching
            # those.

            # note for version/aida cpuid info/motherboard info there's a space
            # between the colon separating labels and values. for some kinds of
            # data, AIDA reports an empty string for value, leading to a line
            # like `{label}   : `. so trim that off when reading values.
            if state == ParseState.VERSION:
                for wanted_prefix, desc in version_lines.items():
                    if line.startswith(wanted_prefix):
                        self.version[desc] = line[len(wanted_prefix) + 1:]
                        parsed = True
                        break
            elif state == ParseState.AIDA_CPUID:
                for wanted_prefix, desc in aida_cpu_lines.items():
                    if line.startswith(wanted_prefix):
                        self.aida_cpuid[desc] = line[len(wanted_prefix) + 1:]
                        parsed = True
                        break
            elif state == ParseState.MOTHERBOARD:
                for wanted_prefix, desc in motherboard_lines.items():
                    if line.startswith(wanted_prefix):
                        self.motherboard[desc] = line[len(wanted_prefix) + 1:]
                        parsed = True
                        break
            elif state == ParseState.MSRS:
                # TODO: ignore MSR lines.. for now.
                parsed = True
                break
            elif state == ParseState.CPUID:
                if line.startswith("allcpu: "):
                    core_location = re.match(
                        "allcpu: Package (\d+) / Core (\d+) / Thread (\d+): (.*)",
                        line
                    )
                    if core_location:
                        cpuid_buf["location"] = {
                            "package": int(core_location.group(1)),
                            "core": int(core_location.group(2)),
                            "thread": int(core_location.group(3))
                        }
                        parsed = True
                    elif line == "allcpu: Valid":
                        if self.guessing_cpu_nr:
                            guessed_nr = self.guessed_cpu_nr
                        else:
                            # if we're not guessing cpu numbers, it might just
                            # be a single cpu?
                            guessed_nr = 0

                        cpuid_buf["location"] = {
                            "package": 0,
                            "core": guessed_nr,
                            "thread": 0
                        }
                        parsed = True
                    elif line == "allcpu: Valid, Virtual":
                        # this one's annoying. for example,
                        # `GenuineIntel00106A4_Bloomfield_CPUID.txt`
                        # there are "Logical CPU #<n>" headers, but no
                        # header describing which CPUs are related to which.
                        # instead, the second half of CPUs are described as
                        # "Valid, Virtual" which probably means the SMT sibling.
                        #
                        # not sure if there are ever cases of sibling cores
                        # being interwoven or if these cases are always
                        # `[core0smt0] [core1smt0] [core0smt1] [core1smt1]` etc
                        # so for these, the core number is inaccurate. sorry!
                        self.inaccurate_core_number = True
                        if self.guessing_cpu_nr:
                            guessed_nr = self.guessed_cpu_nr
                        else:
                            # if we're not guessing cpu numbers, it might just
                            # be a single cpu?
                            guessed_nr = 0

                        cpuid_buf["location"] = {
                            "package": 0,
                            "core": guessed_nr,
                            "thread": 1
                        }
                        parsed = True
                    else:
                        raise Exception("bad allcpu line: {}".format(line))
                else:
                    # it's a line like `CPUID [0-9A-F]{8}: {regs}`?
                    pat = """CPUID ([0-9A-F]{8}): ([0-9A-F]{8})-([0-9A-F]{8})-([0-9A-F]{8})-([0-9A-F]{8})( .*)?"""

                    # some AMD summaries use space separators instead of hypen?
                    amd_quirk_pat = """CPUID ([0-9A-F]{8}): ([0-9A-F]{8}) ([0-9A-F]{8}) ([0-9A-F]{8}) ([0-9A-F]{8})( .*)?"""

                    # `AuthenticAMD0500F20_K14_Bobcat_CPUID.txt` has the colon
                    # in a weird spot.
                    bobcat_quirk_pat = """CPUID ([0-9A-F]{8}) :([0-9A-F]{8})-([0-9A-F]{8})-([0-9A-F]{8})-([0-9A-F]{8})( .*)?"""

                    # or otherwise, maybe it's `CPUID  \t{regs}`. some older
                    # Intel CPUID readings were like that.
                    altpat = """CPUID ([0-9A-F]{8})\s+([0-9A-F]{8})-([0-9A-F]{8})-([0-9A-F]{8})-([0-9A-F]{8})( .*)?"""
                    leaf_info = re.match(pat, line)
                    if not leaf_info:
                        leaf_info = re.match(altpat, line)
                    if not leaf_info:
                        leaf_info = re.match(amd_quirk_pat, line)
                    if not leaf_info:
                        leaf_info = re.match(bobcat_quirk_pat, line)
                    if leaf_info:
                        subleaf = None
                        try:
                            misc_info = leaf_info.group(6)
                            infos = re.findall(" \[[^]]+\]", misc_info)
                            for info in infos:
                                sl = re.match(" \[SL ([0-9A-F]+)\]", info)
                                if sl:
                                    subleaf = int(sl.group(1), 16)
                        except:
                            # `group(6)` raised an exception because there's no
                            # group. that's fine, just no subleaf.
                            pass
                        leaf = int(leaf_info.group(1), 16)
                        leaf_record = {
                            "eax": int(leaf_info.group(2), 16),
                            "ebx": int(leaf_info.group(3), 16),
                            "ecx": int(leaf_info.group(4), 16),
                            "edx": int(leaf_info.group(5), 16)
                        }
                        if subleaf is not None:
                            if self.guessing_cpuid_subleaf_nr == None:
                                # we have suffixes like `[ SL 01 ]` telling us
                                # which subleaf was queried
                                self.guessing_cpuid_subleaf_nr = False

                            if self.guessing_cpuid_subleaf_nr == True:
                                # at some point in the past we guessed there are
                                # implicit subleaves because there were
                                # duplicate rows. now we're finding there are SL
                                # suffixes for subleaf numbers. so the guess in
                                # the past was at best premature and at worst
                                # wrong. raise an error, though we don't
                                # remember which leaf had duplicate entries.
                                raise Exception("""duplicate cpuid leaves in \
                                    {}""".format(sys.argv[3]))

                            if leaf not in cpuid_buf:
                                cpuid_buf[leaf] = {}
                            else:
                                if subleaf in cpuid_buf[leaf]:
                                    allow_conflict = False

                                    # what the hell, right?
                                    # `AuthenticAMD0630F01_K15_Berlin_00_CPUID.txt`
                                    # does this. one subleaf is duplicated on
                                    # each core, and the duplicate record
                                    # matches the previous entry. so just allow
                                    # it. whyyyyyyy
                                    if leaf == 0xd and subleaf == 0x3e and \
                                        cpuid_buf[leaf][subleaf] == leaf_record:
                                            allow_conflict = True

                                    if not allow_conflict:
                                        # if there is a conflict and we have
                                        # reason to believe there is a specific
                                        # subleaf number without guessing, just
                                        # bail out.
                                        # this is probably bad data.
                                        raise Exception(
                                            """duplicate cpuid subleaf: \
                                            {}/{} {}""".format(leaf, subleaf,
                                                sys.argv[3]))
                            cpuid_buf[leaf][subleaf] = leaf_record
                        else:
                            if leaf in cpuid_buf:
                                # if there is no suffix reporting subleaves,
                                # guess them ourselves.
                                if self.guessing_cpuid_subleaf_nr == None:
                                    # not sure one way or the other yet. say
                                    # implicit subleaves...
                                    self.guessing_cpuid_subleaf_nr = True
                                elif self.guessing_cpuid_subleaf_nr == False:
                                    raise Exception(
                                        "duplicate cpuid leaf: {} - {}".format(
                                            sys.argv[3], leaf))

                                # ok, now for the fun. at this leaf we have
                                # either a single entry we need to promote to a
                                # subleaf table, or a subleaf table. if it's a
                                # subleaf table it's keyed by integers,
                                # otherwise it's keyed by eax/ebx/ecx/edx.
                                if "eax" in cpuid_buf[leaf]:
                                    # promote this to a subleaf table
                                    subleaves = {}
                                    subleaves[0] = cpuid_buf[leaf]
                                    cpuid_buf[leaf] = subleaves
                                    # this means that the leaf we're looking at
                                    # is presumed to be the first subleaf
                                    self.guessed_cpuid_subleaf_nr = 1

                                cpuid_buf[leaf][
                                    self.guessed_cpuid_subleaf_nr
                                ] = leaf_record
                                self.guessed_cpuid_subleaf_nr += 1
                            else:
                                cpuid_buf[leaf] = leaf_record
                        parsed = True
                    else:
                        # might be the AIDA summary of cache info...
                        if re.match("L\d .*Cache:", line):
                            # yep. understood and don't care..
                            parsed = True

            if parsed:
                continue
            else:
                state = ParseState.HEADER

            if state == ParseState.HEADER:
                for k, (next_name, next_state) in section_headers.items():
                    if line == k:
                        name = next_name
                        state = next_state
#                        print("state: {}".format(name))
                        parsed = True
                        break
                    # TODO: some AIDA versions only read MSRs from one(?) core
                    # and have one MSR Registers region as a result.
                    # not sure what to do with that (yet)
                    else:
                        # header might be a regex, try that
                        match = re.match(k, line)
                        if match:
                            # TODO: HACK: don't handle the remainder correctly
                            # yet
                            if k == "PerformanceFrequency =.*":
                                parsed = True
                                state = ParseState.DONE
                                break
                            # TODO: HACK: handle weird lines in Ryzen Z1 cpuid
                            if line.startswith("Group: 0x00 Affinity mask: "):
                                # see above about this pattern. guess CPU
                                # numbers...
                                self.inaccurate_core_number = True
                                if not self.guessing_cpu_nr:
                                    self.guessing_cpu_nr = True
                                    self.guessed_cpu_nr = 0
                                else:
                                    self.guessed_cpu_nr += 1

                                cpunum = self.guessed_cpu_nr
                            else:
                                # yep, that was it. currently the regexes all
                                # have one \d+ group for the cpu/thread number
                                # the header describes.
                                cpunum = int(match.group(1))
                                if self.first_data_line and cpunum == 1:
                                    self.cpus_start_counting_from_1 = True

                                if self.cpus_start_counting_from_1:
                                    cpunum -= 1

                            if re.match("CPUID Registers \(CPU .* Virtual\)",
                                    line):
                                self.inaccurate_core_number = True

                            name = next_name
                            state = next_state
                            if next_state == ParseState.CPUID:
                                self.cpuid[cpunum] = {}
                                cpuid_buf = self.cpuid[cpunum]
                            else:
                                # non-cpuid state up next. probably MSRs.
                                # HELP! handle MSRs!!!
                                pass
                            parsed = True
                            break

            if not parsed:
                raise Exception("unhandled line: {}".format(line))
        # read ------[ Versions ]------

        if 0 not in self.cpuid:
            raise Exception("what's up in {}".format(sys.argv[1]))
        if 0x80000002 in self.cpuid[0]:
            leaf1 = self.cpuid[0][0x80000002]
            leaf2 = self.cpuid[0][0x80000003]
            leaf3 = self.cpuid[0][0x80000004]
            s = struct.pack("<IIIIIIIIIIII",
                leaf1["eax"], leaf1["ebx"], leaf1["ecx"], leaf1["edx"], 
                leaf2["eax"], leaf2["ebx"], leaf2["ecx"], leaf2["edx"], 
                leaf3["eax"], leaf3["ebx"], leaf3["ecx"], leaf3["edx"]
            ).decode("utf-8").rstrip("\x00").rstrip(" ")

            # there are two Van Gogh AMD APUs that have a newline at the end of
            # their processor brand string.
            s = s.strip()

            self.cpuid_name = s
        else:
            self.cpuid_name = None

        self.parsed_features = []
        for feature in FEATURES:
            parsed = feature.parse(self, db)
            if parsed:
                self.parsed_features.append(parsed)

def init_db(dbpath):
    connection = sqlite3.connect("{}".format(dbpath))
    connection.cursor().executescript(open("product_info.sql", "r").read())

def add(dbpath, cpuid_filename):
    if not os.path.isfile(dbpath):
        init_db(dbpath)

    text = open(cpuid_filename, "r").readlines()
    db = dataset.connect("sqlite:///{}".format(dbpath))

    info = AIDAInfo(db, text)

    cpu_table = db['cpus']

    cpu_features = db['cpu_features']

    if cpu_table.find_one(name=info.proc_name(),
            virtual=info.suspected_virtual()):
#        print("'{}' already exists?".format(info.proc_name()))
        sys.exit(0)

    fam_id = info.feature("family").value

    uarch_id = info.feature("uarch").value

    first_cpu_info = info.cpuid[0]
    leaf_0h = first_cpu_info[0]
    cpu_id = cpu_table.insert({
        "name": info.proc_name(),
        "cpuid_fms": leaf_0h['eax'],
        "family": fam_id,
        "uarch": uarch_id,
        "source": cpuid_filename,
        "virtual": info.suspected_virtual(),
    })

    for feat in info.parsed_features:
        if feat.present:
            db_feat = db['features'].find_one(
                    name=feat.shortname, value=feat.value)
            if not db_feat:
                feat_id = db['features'].insert({
                    "name": feat.shortname,
                    "value": feat.value,
                })
            else:
                feat_id = db_feat['id']

            cpu_features.insert({
                "cpu": cpu_id,
                "feature": feat_id
            })

def get_interesting(features):
    predicate = ' and '.join(
        ["cpus.id in has_{}".format(
            f['name'].replace(" ", "SP")) for f in features]
    )
    interesting_ctes = """
    interesting as (
        select cpus.id from cpus where
            {}
    ),
    not_interesting as (
        select cpus.id from cpus where
            cpus.id not in interesting
    )
    """
    return interesting_ctes.format(predicate)

def get_predicate_cte(featrule):
    mangled = featrule['name'].replace(" ", "SP")
    print(featrule['name'])
    return """
        has_{} as (
            select cpu_features.cpu from cpu_features
                join features on cpu_features.feature=features.id
            where features.name="{}" and features.value{}"{}"
        ),""".format(mangled, featrule['name'], featrule['op'],
                featrule['value'])

def get_interesting_ctes(features):
    pat = "([A-Za-z0-9 ]+)(:?(=|!=|>|<|>=|<=)([A-Za-z0-9]+))?"

    feature_rules = []

    for feat in features:
        feature_parse = re.match(pat, feat)

        if not feature_parse:
            raise Exception("can't parse feature test: '{}'".format(feat))

        name = feature_parse.group(1)

        op = feature_parse.group(3)
        value = feature_parse.group(4)

        if op is None:
            op = "!="

        if value is None:
            value = "0"

        feature_rules.append({ "name": name, "op": op, "value": value })

    predicates = [get_predicate_cte(feat) for feat in feature_rules]

    return "with " + "".join(predicates) + get_interesting(feature_rules)

def cpus_with_query(features):
    return get_interesting_ctes(features) + \
        """ select distinct cpus.id, cpus.name from cpus \
        where cpus.id in interesting;"""

def cpus_without_query(features):
    return get_interesting_ctes(features) + \
        """ select distinct cpus.id, cpus.name from cpus \
        where cpus.id in not_interesting;"""

def families_with_query(features):
    return get_interesting_ctes(features) + \
        """ select distinct families.id, families.name from cpus join families \
        on cpus.family=families.id where cpus.id in interesting;"""

def families_without_query(features):
    return get_interesting_ctes(features) + \
        """ select distinct families.id, families.name from cpus join families \
        on cpus.family=families.id where cpus.id in not_interesting;"""


def families_transitioning_query(features):
    return get_interesting_ctes(features) + \
        """ select * from families where
            families.id in interesting and
            families.id in not_interesting;"""

def families_with(dbpath, features):
    db = dataset.connect("sqlite:///{}".format(dbpath))
    families = db.query(families_with_query(features))
    for family in families:
        print(family['name'])

def families_without(dbpath, features):
    db = dataset.connect("sqlite:///{}".format(dbpath))
    families = db.query(families_without_query(features))
    for family in families:
        print(family['name'])

def families_transitioning(dbpath, features):
    db = dataset.connect("sqlite:///{}".format(dbpath))
    families = db.query(families_transitioning_query(features))
    for family in families:
        print(family['name'])

def cpus_with(dbpath, features):
    db = dataset.connect("sqlite:///{}".format(dbpath))
    cpus = db.query(cpus_with_query(features))
    for cpu in cpus:
        print(cpu['name'])

def cpus_without(dbpath, features):
    db = dataset.connect("sqlite:///{}".format(dbpath))
    cpus = db.query(cpus_without_query(features))
    for cpu in cpus:
        print(cpu['name'])


cmd = sys.argv[1]

if cmd == "add":
    add(sys.argv[2], sys.argv[3])
elif cmd == "cpus-with":
    cpus_with(sys.argv[2], sys.argv[3:])
elif cmd == "cpus-without":
    cpus_without(sys.argv[2], sys.argv[3:])
elif cmd == "families-with":
    families_with(sys.argv[2], sys.argv[3:])
elif cmd == "families-without":
    families_without(sys.argv[2], sys.argv[3:])
elif cmd == "families-transitioning":
    families_transitioning(sys.argv[2], sys.argv[3:])
