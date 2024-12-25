from enum import Enum
import re
import sys
import struct

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

class CPUIDFeature:
    def __init__(self, shortname, longname, reg, offset, width, leaf,
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
            return self
        top_level = info.cpuid[0][self.leaf]
        leaf = None
        if self.subleaf:
            leaf = top_level[self.subleaf]
        else:
            leaf = top_level

        reg = leaf[self.reg]

        bits = (reg >> self.offset) & ((1 << self.width) - 1)

        self.value = bits

        return self

    def show(self):
        return "{}: {:x}".format(self.shortname, self.value)

    def __str__(self):
        if self.value:
            return self.show()
        else:
            return "-{}".format(self.shortname)

class CPUIDBoolFeature(CPUIDFeature):
    def __init__(self, shortname, longname, reg, offset, leaf, subleaf=None):
        super().__init__(shortname, longname, reg, offset, 1, leaf, subleaf)

    def show(self):
        if self.value == 1:
            return self.shortname

FEATURES = [
    CPUIDBoolFeature("ARAT", "Always Running APIC Timer", "eax", 2, 0x00000006)
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
                                # see above about this pattern. guess CPU numbers...
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
            self.cpuid_name = s
        else:
            self.cpuid_name = None

        self.parsed_features = []
        for feature in FEATURES:
            parsed = feature.parse(self)
            if parsed:
                self.parsed_features.append(parsed)

# text = open("./InstLatx64/AuthenticAMD/AuthenticAMD0870F10_K17_Matisse_11_CPUID.txt", "r").readlines()
text = open(sys.argv[1], "r").readlines()
# print(text)

info = AIDAInfo(text)
# print(info.version)
if "synth_type" in info.aida_cpuid:
    if "alias" in info.aida_cpuid:
        print("{}: {}".format(info.aida_cpuid["alias"], info.aida_cpuid["synth_type"]))
    else:
        print("{}".format(info.aida_cpuid["synth_type"]))
elif info.cpuid_name:
    print("{} (no AIDA banner)".format(info.cpuid_name))
else:
    print("{} (cannot summarize)".format(sys.argv[1]))
# print(info.motherboard)
# print(info.cpuid[1])
for feat in info.parsed_features:
    print("- ", feat)
