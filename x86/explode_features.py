from enum import Enum
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

    def parse(self, info):
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
        if self.subleaf:
            leaf = top_level[self.subleaf]
        else:
            leaf = top_level

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

class CPUIDBoolFeature(CPUIDFeature):
    def __init__(self, shortname, longname, leaf, reg, offset, subleaf=None):
        super().__init__(shortname, longname, leaf, reg, offset, 1, subleaf)

    def present(self):
        return self.value == 1

    def show(self):
        if self.value == 1:
            return self.shortname

CPU_UARCH_INFO = {
    "Am486": {
        "name": "Am486"
    },
    # the Am5x86 is reportedly an Am486 with some improvements (cache, process
    # improvements leading to higher clocks).
    "Am5x86": {
        "name": "Am486",
        "first": "1995-11-01"
    },
    "K5": {
        "name": "K5",
        "family": "K5",
    },
    "K6": {
        "name": "K6",
        "family": "K6"
    },
    "K6-2": {
        "name": "K6-2",
        "family": "K6"
    },
    "K6-III": {
        "name": "K6-III",
        "family": "K6"
    },
    "K6-III+": {
        "name": "K6-III+",
        "family": "K6"
    },
    "K7": {
        "name": "K7",
        "family": "K7"
    },
    "K7": {
        "name": "K7",
        "family": "K7"
    },
    "K75": {
        "name": "K75",
        "family": "K7"
    },
    "Morgan": {
        "name": "Morgan",
        "family": "K7"
    },
    "Palomino": {
        "name": "Palomino",
        "family": "K7"
    },
    "Spitfire": {
        "name": "Spitfire",
        "family": "K7"
    },
    "Thoroughbred": {
        "name": "Thoroughbred",
        "family": "K7"
    },
    "Thunderbird": {
        "name": "Thunderbird",
        "family": "K7"
    },
    "Barton": {
        "name": "Barton",
        "family": "K7"
    },
    "K8": {
        "name": "K8",
        "family": "K8"
    },
    "ClawHammer": {
        "name": "ClawHammer",
        "family": "K8"
    },
    "SledgeHammer": {
        "name": "SledgeHamer",
        "family": "K8"
    },
    "Winchester": {
        "name": "Winchester",
        "family": "K8"
    },
    "Manchester": {
        "name": "Manchester",
        "family": "K8"
    },
    # allegedly a wholly different design focused on low-power applications.
    # could use better citations...
    "Bobcat": {
        "name": "Bobcat",
        "family": "Bobcat"
    },
    "Jaguar": {
        "name": "Jaguar",
        "family": "Jaguar"
    },
    "Cato": {
        "name": "Cato",
        "family": "Jaguar"
    },
    "Puma": {
        "name": "Puma",
        "family": "Jaguar"
    },
    "K10": {
        "name": "K10",
        "family": "K10"
    },
    "Puma (2008)": {
        "name": "Puma (2008)",
        "family": "K10"
    },
    # the first of the AMD64 Opterons!
    "Barcelona": {
        "name": "Barcelona",
        "family": "K10"
    },
    # first Phenom II
    "Thuban": {
        "name": "Thuban",
        "family": "K10"
    },
    # Phenom II, and some Athlon X2
    "Deneb": {
        "name": "Deneb",
        "family": "K10"
    },
    # Phenom II (later on), some Athlon X2
    "Regor": {
        "name": "Regor",
        "family": "K10"
    },
    # more Opteron
    "Istanbul": {
        "name": "Istanbul",
        "family": "K10"
    },
    # end of the K10 Opteron era
    "Magny-Cours": {
        "name": "Magny-Cours",
        "family": "K10"
    },
    "Bulldozer": {
        "name": "Bulldozer",
        "family": "Bulldozer"
    },
    "Excavator": {
        "name": "Excavator",
        "family": "Bulldozer"
    },
    "Piledriver": {
        "name": "Piledriver",
        "family": "Bulldozer"
    },
    "Steamroller": {
        "name": "Steamroller",
        "family": "Bulldozer"
    },
    "Zen": {
        "name": "Zen",
        "family": "Zen"
    },
    "Zen 2": {
        "name": "Zen 2",
        "family": "Zen"
    },
    "Zen 3": {
        "name": "Zen 3",
        "family": "Zen 3"
    },
    "Zen 4": {
        "name": "Zen 4",
        "family": "Zen 3"
    },
    "Zen 4c": {
        "name": "Zen 4c",
        "family": "Zen 3"
    },
    "Zen 5": {
        "name": "Zen 5",
        "family": "Zen 3"
    }
}

CPU_FAMILY_INFO = {
    "Am486": {
        "name": "Am486"
    },
    "K5": {
        "name": "K5"
    },
    "K6": {
        "name": "K6"
    },
    "K7": {
        "name": "K7"
    },
    "K8": {
        "name": "K8"
    },
    "K10": {
        "name": "K10"
    },
    "Bobcat": {
        "name": "Bobcat"
    },
    "Jaguar": {
        "name": "Jaguar"
    },
    "Bulldozer": {
        "name": "Bulldozer"
    },
    "Zen": {
        "name": "Zen"
    },
    "Zen 3": {
        "name": "Zen 3"
    },
}

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

    def parse(self, info):
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

    def parse(self, info):
        if 0x00000000 not in info.cpuid[0]:
            return None

        brand = info.cpuid[0][0x00000000]

        vendorname = info.feature("vendor").value

        uarch_fam = None

        if vendorname == "AuthenticAMD":
            uarch_fam = self.parse_amd(info)
        elif vendorname == "GenuineIntel":
            uarch_fam = self.parse_intel(info)
#        else:
#            print("""cannot currently handle processors from vendor \
#                    {}""".format(vendorname))

        if uarch_fam is None:
            return

        if "uarch" in uarch_fam:
            info.add_feature(ParsedFeature(
                "uarch", "CPUID-implied processor architecture",
                uarch_fam["uarch"]
            ))

        if "family" in uarch_fam:
            info.add_feature(ParsedFeature(
                "family", "CPUID-implied processor family", uarch_fam["family"]
            ))


    def parse_intel(self, info):
        return None
#         raise Exception("Intel not supported yet")

    def parse_amd(self, info):
        family = info.feature("FamilyID").value
        ext_family = info.feature("ExtendedFamilyID").value
        if ext_family:
            family += ext_family

        model = info.feature("ModelID").value
        ext_model = info.feature("ExtendedModelID").value
        if ext_model:
            model += ext_model

        # upsettingly, sources here are scant. Todd Allen's `cpuid` describes
        # all K6 family processors as K6 uarch, but with more specific synthetic
        # family names. for most purposes i'm concerned about, uarch revisions,
        # such as K6, K6-2, K6-III, should be distinct. similarly, revisions
        # through the Athlon years are very informative, and on and on.
        #
        # pages like Wikipedia's `List of AMD K6 processors` are heavily sourced
        # from cpu-world.com/CPUs/*, whose pages currently return text like:
        # > Specifications pages and related web pages were taken down due to
        # > ongoing content scraping.
        # >
        # > The pages will be back online once scraping stops.
        #
        # great.
        #
        # simultaneously, en.wikichip.org has been down for two weeks so it's
        # not trivial to crosscheck any descriptions there either.
        #
        # great.
        #
        # so, at a high level this is informed by Todd Allen's descriptions,
        # partially cross-checked by the "CPU Alias" reported by EVEREST or AIDA
        # if a header is available in InstLatx64 dumps, as well as some checking
        # against pages via internet archive.

        # "uarch" and "family" are mushy distinctions. "uarch" tries to hew more
        # closely to an actual description of a physical core that ships in a
        # real product. "family" is a mushier distinction, which might be best
        # described as a "descends-from" relationship. one could of course say
        # that everything descends from the 8086 (or 8080, or 4004, or ..), but
        # this is too broad to be truly informative. so "family" here is a fuzzy
        # line like "more comprehensive change than just adding/expanding
        # caches". practically speaking, for AMD cases, "family" in cpuid
        # reflects this pretty well and tracks with their own branding/marketing
        # of products.

        amd_fm_uarchs = {
            (4, 3): { "uarch": "Am486" },
            (4, 7): { "uarch": "Am486" },
            (4, 8): { "uarch": "Am486" },
            (4, 9): { "uarch": "Am486" },
            # https://datasheets.chipdb.org/AMD/486_5x86/19751C.pdf
            # page 56 describes CPUID model/family bits for AMD 5x86
            # processors. this is slightly more precise than `cpuid`.
            (4, 0xe): { "uarch": "Am5x86" },
            (4, 0xf): { "uarch": "Am5x86" },
            0x4: { "family": "K5" },
            # cpu-world.com and EVEREST agree F=5/M={0,1} is K5
            # cpuid does not mention these
            (5, 0): { "uarch": "K5" },
            (5, 1): { "uarch": "K5" },
            # cpu-world.com, EVEREST, and cpuid all agree these are K6
            # though.
            (5, 6): { "uarch": "K6", "family": "K6" },
            (5, 7): { "uarch": "K6", "family": "K6" },
            # back on our own..
            (5, 8): { "uarch": "K6-2", "family": "K6" },
            (5, 9): { "uarch": "K6-III", "family": "K6" },
            # what about models a-c?
            # "K6-2+" was also family 5/model D, donthough InstLatx64 has
            # one record of a K6-2+ which can be distinguished only by
            # stepping (4, rather than 0). not bothering with that
            # distiction here.
            (5, 0xd): { "uarch": "K6-III+", "family": "K6" },
            0x5: { "family": "K6" },
            (6, 1): { "uarch": "K7", "family": "K7" },
            (6, 2): { "uarch": "K75", "family": "K7" },
            (6, 3): { "uarch": "Spitfire", "family": "K7" },
            (6, 4): { "uarch": "Thunderbird", "family": "K7" },
            (6, 6): { "uarch": "Palomino", "family": "K7" },
            (6, 7): { "uarch": "Morgan", "family": "K7" },
            # InstLatx86 has a Thoroughbred as stepping 0, Appelbred as
            # stepping 1. no stepping distinguisher here though, yet
            (6, 8): { "uarch": "Thoroughbred", "family": "K7" },
            (6, 10): { "uarch": "Barton", "family": "K7" },
            0x6: { "family": "K7" },
            # reportedly K8 and K7 are very similar, just that K8 also has
            # the minor addition of "x86-64". i've not found much to
            # substantiate this, so [citation needed] as it were.
            (0xf, 0x4): { "uarch": "ClawHammer", "family": "K8" },
            (0xf, 0x5): { "uarch": "SledgeHamer", "family": "K8" },
            # etallen's `cpuid` lists more entries here, but InstLatx64's
            # cpuid collection doesn't have samples to check against, so
            # skipping forward a few..

            # cpuid leaf 1 eax has `2` in Extended Model ID but model is
            # <0xf?
            (0xf, 0xb): { "uarch": "Manchester", "family": "K8" },
            # notably cpuid leaf 1 eax has a `1` in Extended Model ID for
            # this sample, but the model is 0xc rather than 0xf, so extended
            # model should be unused..?
            (0xf, 0xc): { "uarch": "Winchester", "family": "K8" },
            # "AuthenticAMD0010FF0_K8_Palermo_CPUID.txt" claims to be
            # Palermo, but so does 00020FC2. and Venice claims to be
            # 00020FF0.
            0xf: { "family": "K8" },
            # K10 is a really great example of how "uarch" is reductive,
            # probably should just use the word "model", or swap "family" and
            # "uarch" though that might conflict with what The Rest Of The World
            # means by those things. these processors' *cores* are all largely
            # the same (e.g. "K10"), and the variation between them seems to be
            # more due to process changes (transistor size shrining, changes to
            # whatever the predecessor to the SMU/PSP were). Turbo core was
            # added in the K10 family of parts but that also is not a core
            # change so much as a "microcontroller controlling the core"..
            #
            # another problem that's really dramatic in the K10 era is that
            # production parts have the same family/model for different product
            # segments. family 10h model 2 is *not* just "Opteron", but to
            # detect exactly which segment a processor is in you apparently need
            # to consult the brand string to know Opteron, Athlon, etc
            (0x10, 0): { "uarch": "", "family": "K10" },
            (0x10, 2): { "uarch": "Barcelona", "family": "K10" },
            (0x10, 4): { "uarch": "Deneb", "family": "K10" },
            (0x10, 5): { "uarch": "", "family": "K10" },
            (0x10, 6): { "uarch": "Regor", "family": "K10" },
            (0x10, 8): { "uarch": "Istanbul", "family": "K10" },
            (0x10, 9): { "uarch": "Magny-Cours", "family": "K10" },
            (0x10, 10): { "uarch": "Thuban", "family": "K10" },
            # not sure InstLatx64 has samples here.. wikipedia also notes these
            # as "Turion X2 Ultra
            0x11: { "uarch": "Puma (2008)", "family": "K10" },
            # double check A8-3850
            0x12: { "uarch": "Puma (2008)", "family": "K10" },
            0x14: { "uarch": "Bobcat", "family": "Bobcat" },
            # iteration on Bobcat, still all distinct from the construction
            # machine architectures.
            (0x16, 0): { "uarch": "Jaguar", "family": "Jaguar" },
            # not widely released..
            (0x16, 2): { "uarch": "Cato", "family": "Jaguar" },
            (0x16, 8): { "uarch": "Cato", "family": "Jaguar" },
            # distinct from the model 11h Puma! this was more widely shipping.
            (0x16, 3): { "uarch": "Puma", "family": "Jaguar" },

            # bulldozer/piledriver/steamroller/excavator
            (0x15, 0): { "uarch": "Bulldozer", "family": "Bulldozer" },
            (0x15, 1): { "uarch": "Piledriver", "family": "Bulldozer" },
            # double check. FX-8350
            (0x15, 2): { "uarch": "Piledriver", "family": "Bulldozer" },
            (0x15, 3): { "uarch": "Steamroller", "family": "Bulldozer" },
            (0x15, 4): { "uarch": "Steamroller", "family": "Bulldozer" },
            (0x15, 6): { "uarch": "Excavator", "family": "Bulldozer" },
            (0x15, 7): { "uarch": "Excavator", "family": "Bulldozer" },

            # double check. A12-9800 etc
            (0x15, 0xb): { "uarch": "Excavator", "family": "Bulldozer" },

            # Zen and onward. this is a bit funky because AMD describes Zen,
            # Zen_, and Zen 2 together in "Revision Guide for AMD Family 17h
            # Models 00h-0Fh Processors" publication 55449. evidence towards
            # their similarity, i suppose?
            # anyway, `cpuid`'s approach is to encode which specific models were
            # which architecture, probably good enough here too.
            (0x17, 0): { "uarch": "Zen", "family": "Zen" },
            (0x17, 1): { "uarch": "Zen", "family": "Zen" },
            (0x17, 2): { "uarch": "Zen", "family": "Zen" },
            (0x17, 3): { "uarch": "Zen 2", "family": "Zen" },
            # other fam 17h models not mentioned above are... probably Zen 2?
            0x17: { "uarch": "Zen 2", "family": "Zen" },

            # mostly by vibes: Zen 3 seems distinct enough from Zen/Zen 2 to be
            # a new "family".
            (0x19, 0): { "uarch": "Zen 3", "family": "Zen 3" },
            # though Zen 4 was a refresh on Zen 3 rather than substantially
            # different
            (0x19, 1): { "uarch": "Zen 4", "family": "Zen 3" },
            (0x19, 2): { "uarch": "Zen 3", "family": "Zen 3" },
            (0x19, 3): { "uarch": "Zen 3", "family": "Zen 3" },
            (0x19, 4): { "uarch": "Zen 3", "family": "Zen 3" },
            (0x19, 5): { "uarch": "Zen 3", "family": "Zen 3" },
            (0x19, 6): { "uarch": "Zen 4", "family": "Zen 3" },
            (0x19, 7): { "uarch": "Zen 4", "family": "Zen 3" },
            (0x19, 8): { "uarch": "Zen 4", "family": "Zen 3" },
            (0x19, 9): { "uarch": "Zen 4", "family": "Zen 3" },
            (0x19, 10): { "uarch": "Zen 4c", "family": "Zen 3" },


            # at least Ryzen 9 7940H w/ Radeon 780M?
            (0x19, 11): { "uarch": "Zen 4", "family": "Zen 3" },
            # at least Ryzen 9 7940H
            (0x19, 12): { "uarch": "Zen 4", "family": "Zen 3" },
            # at least Ryzen 7 8700G
            (0x19, 13): { "uarch": "Zen 4", "family": "Zen 3" },
            (0x19, 15): { "uarch": "Zen 4", "family": "Zen 3" },

            # allegedly a "ground up redesign" of zen 3, i don't know how
            # similar or different this is from zen 3/4 yet though.
            (0x1a, 0): { "uarch": "Zen 5", "family": "Zen 3" },
            (0x1a, 1): { "uarch": "Zen 5", "family": "Zen 3" },
            (0x1a, 2): { "uarch": "Zen 5", "family": "Zen 3" },
            (0x1a, 3): { "uarch": "Zen 5", "family": "Zen 3" },
            (0x1a, 4): { "uarch": "Zen 5", "family": "Zen 3" },
            (0x1a, 5): { "uarch": "Zen 5", "family": "Zen 3" },
            (0x1a, 6): { "uarch": "Zen 5", "family": "Zen 3" },
            (0x1a, 7): { "uarch": "Zen 5", "family": "Zen 3" },
            (0x1a, 8): { "uarch": "Zen 5", "family": "Zen 3" },

        }

        if (family, model) in amd_fm_uarchs:
            return amd_fm_uarchs[(family, model)]
        elif family in amd_fm_uarchs:
            return amd_fm_uarchs[family]
        else:
            print("unknown family and/or model: {:x}h/{:x}h".format(family,
                model))
            print("  {}".format(info.cpuid_name))
            return { "family": "unknown ({:x})/{:x})".format(family, model) }

FEATURES = [
    CPUIDBoolFeature("PCLMULDQ", "PCLMULDQ", 0x00000001, "ecx", 1),
    CPUIDBoolFeature("TscInvariant", """TSC runs at a constant frequency in all \
            P- and C-states""", 0x80000007, "edx", 8),
    CPUIDBoolFeature("ARAT", "Always Running APIC Timer", 0x00000006, "eax", 2),
    CPUIDFeature("ExtendedFamilyID", "Extended Family ID", 0x00000001, "eax", 20,
        4),
    CPUIDFeature("ExtendedModelID", "Extended Model ID", 0x00000001, "eax", 16,
        4),
    CPUIDFeature("FamilyID", "Family ID", 0x00000001, "eax", 8, 4),
    CPUIDFeature("ModelID", "Model ID", 0x00000001, "eax", 4, 4),

    CPUIDFeature("TSC:CLK (denominator)", "", 0x00000015, "eax", 0, 32),
    CPUIDFeature("TSC:CLK (numerator)", "", 0x00000015, "ebx", 0, 32),
    CPUIDFeature("base CCLK", "", 0x00000016, "eax", 0, 16),
    CPUIDFeature("max CCLK", "", 0x00000016, "ebx", 0, 16),

    CPUIDBoolFeature("Virtualized", "Running on a virtual processor",
        0x00000001, "ecx", 31),
    CPUIDFeature("Hypervisor leaves", "Microsoft Hypervisor CPUID leaves",
        0x00000001,"eax", 0, 32),

    CPUIDBoolFeature("monitor", "monitor/mwait instructions",
        0x00000001, "ecx", 3),

    CPUIDBoolFeature("Long mode", "Processor supports AMD64 mode",
        0x80000001, "edx", 29),

    CPUIDBoolFeature("DecodeAssist", "SVM helps decode instructions on VMEXIT",
        0x8000000A,"edx", 7),
    CPUIDBoolFeature("AVIC", "SVM has AVIC support",
        0x8000000A,"edx", 13),
    CPUIDBoolFeature("x2AVIC", "SVM has x2AVIC support",
        0x8000000A,"edx", 18),

    CPUIDVendor(),
    CPUIDUarch()
]

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
        if self.cpuid_name:
            return self.cpuid_name
        else:
            family = self.feature("FamilyID").value
            ext_family = self.feature("ExtendedFamilyID").value
            if ext_family:
                family += ext_family

            model = self.feature("ModelID").value
            ext_model = self.feature("ExtendedModelID").value
            if ext_model:
                model += ext_model

            return "Unknown {} family {}h model {}h".format(
                self.feature("vendor"),
                family,
                model
            )

    def __init__(self, text):
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
                                    {}""".format(sys.argv[1]))

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
                                                sys.argv[1]))
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
                                            sys.argv[1], leaf))

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
                            self.cpuid[cpunum] = {}
                            cpuid_buf = self.cpuid[cpunum]
                            parsed = True
                            break

            if not parsed:
                raise Exception("unhandled line: {}, {}".format(line,
                    sys.argv[1]))
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
            parsed = feature.parse(self)
            if parsed:
                self.parsed_features.append(parsed)

def add(dbpath, cpuid_filename):
    text = open(cpuid_filename, "r").readlines()
    db = dataset.connect("sqlite:///{}".format(dbpath))

    info = AIDAInfo(text)

    cpu_features = db['cpu_features']

    if db['cpus'].find_one(name=info.proc_name()):
        print("'{}' already exists?".format(info.proc_name()))
        sys.exit(0)

    fam = info.feature("family")
    fam_id = None
    if fam:
        fam_id = db['families'].find_one(name=fam.value)
        if fam_id is None:
            db['families'].insert(CPU_FAMILY_INFO[fam.value])
        fam_id = db['families'].find_one(name=fam.value)["id"]

    uarch = info.feature("uarch")
    uarch_id = None
    if uarch:
        uarch_id = db['uarches'].find_one(name=uarch.value)
        if uarch_id is None:
            db['uarches'].insert(CPU_UARCH_INFO[uarch.value])
        uarch_id = db['uarches'].find_one(name=uarch.value)["id"]

    first_cpu_info = info.cpuid[0]
    leaf_0h = first_cpu_info[0]
    cpu_id = db['cpus'].insert({
        "name": info.proc_name(),
        "cpuid_fms": leaf_0h['eax'],
        "family": fam_id,
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

def get_interesting(feat_names):
    predicate = ' and '.join(
        ["cpus.id in has_{}".format(f.replace(" ", "SP")) for f in feat_names]
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

def get_predicate_cte(featname):
    mangled = featname.replace(" ", "SP")
    return """
        has_{} as (
            select cpu_features.cpu from cpu_features
                join features on cpu_features.feature=features.id
            where features.name="{}" and features.value="1"
        ),""".format(mangled, featname)

def get_interesting_ctes(features):
    predicates = [get_predicate_cte(feat) for feat in features]

    return "with " + "".join(predicates) + get_interesting(features)

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
