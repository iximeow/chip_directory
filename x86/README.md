## x86 processors and features: tools and documentation

for now, this is mainly oriented around interpreting CPUID bits and making
cross-family statements about feature support in practice.

the complications of this are described below, but in short the ideal state here
would be to know what CPUID readings describe processors in which market
segments, and which processors are unreleased/prerelease versus being
intentional product releases to general (non-OEM) parties.

as an example of this right now, acknowledging that there is no Intel family
info yet and so only descriptive of AMD, you can ask "what processor families
have AVX2?" with...
```
> for f in InstLatx64/AuthenticAMD/AuthenticAMD*CPUID*.txt; do
>   python3 explode_features.py add info.db $f
> done

> python3 explode_features.py families-with info.db AVX2
Zen
Zen 3
```

... for entirely arbitrary reasons, i decided that Zen 2 rounds to Zen, and both Zen 4 and 5 round to Zen 3. this should probably be revisited.

while early/unreleased/OEM configurations are interesting (both technically and
historically), it's much more useful to say for example, "all Zen processors
support ..." than to say "all Zen processors except this early-release
engineering sample two people have".

even so, interpreting a bit's value in an MSR or cPUID (sub)leaf is not always
straightforward; it's the result of an intersection between:

* silicon capability
* microcode support
* BIOS support
* BIOS/OS configuration

while all of these are detailed below, the short of it is that there are two
kinds of longitudinal questions i've found myself asking:

* which hardware, or families of hardware, support a feature of interest?
* which end-user configurations will i find a feature enabled on?

the former is largely an intellectual curiosity question - it informs mental
models of how a part works, and informs how support for such features might be
designed, but promises little about the world i'll find.

the latter is more relevant from a practical engineering perspective - it helps
inform which kinds of features i will find cohabitating and which cases can be
found and tested on which configurations of hardare and software.

to me, both of these are interesting and important! they're just different
questions.

#### on silicon capability (if the feature requires silicon support)

this can vary between processor steppings, and is most likely to be
underrepresented in A0/engineering sample/qualification sample parts. but
*which* silicon's capability? great question!

"microarchitecture" (uarch) often refers to the CPU core which is
processing instructions. but especially as historically-"North Bridge"
functionality like memory controllers and some peripherals have been
intergrated into CPU SoCs, a CPU core's architecture is decreasingly
descriptive when looking at capabilities involving larger parts of the
whole SoC.

in some cases, for example, AMD Zen-era processors are described as
CCX/"CPU dies" and an I/O die. the CCX and I/O dies might change in
different ways at different cadences across product lines - Zen 3 and Zen
4 have fairly similar CPU core architcectures, but the I/O dies between
the two are
[reportedly](https://www.anandtech.com/show/17585/amd-zen-4-ryzen-9-7950x-and-ryzen-5-7600x-review-retaking-the-high-end/6)
quite different.

in Intel processors the distinction is not nearly so dramatic or clean,
but consider integrated graphics processors in Intel SoCs - the graphics
processing architecture is not described at all by a "Gracemont" or
"Golden Cove" CPU microarchitecture. we rarely have words for, let alone
codenames, for these other components.

finally, "silicon" is really intended as a shorthand for "state of a processor
at rest when shipped to a consumer". in this sense, microcode ROM in an Am486 is
effectively "silicon"; it's fixed state that cannot be changed in the field.

additionally, "silicon" may have the transistors or code to support a feature
that is still disabled in the interest of market segmentation. in these cases we
might as well say the silicon doesn't support a feature if that support is fused
off, but as an example this is a additional axis when asking "does a Skylake
processor support ..."

note that market segmentation continues to be an opportunity for further
confusion later on as well.

#### on microcode capability (if the feature requires microcode support)

while some features may be implemented primarily in terms of silicon ("SSE 3"),
many features have some relationship to ""microcode"". here, "microcode" is
meant as a catch-all for field-updatable code or configuration whose behavior is
generally not exposed to end users. "microcode blobs" applied when whatever
operating system boots a computer are generally how this manifests.

on x86 parts there is some initial microcode revision that is included in a ROM
when the processor is assembled, but it's very common for Intel and AMD both to
have microcode updates to fix or work around errata.
[sometimes](https://www.techpowerup.com/329386/amd-quietly-disables-zen-4s-loop-buffer-feature-without-performance-penalty)
microcode updates can result in enabling or disabling whole features on a
processor.

another recent example of this phenomenon, from Intel this time, relates to
`umonitor`/`umwait` instructions: this [MONITOR and UMONITOR Performance
Guidance](https://www.intel.com/content/www/us/en/developer/articles/technical/software-security-guidance/technical-documentation/monitor-umonitor-performance-guidance.html)
page says,

> To address this, affected processors may disable UMONITOR address monitoring
> by default. Disabling UMONITOR address monitoring means that a UMONITOR does
> not set up an address monitor, which may prevent a subsequent UMWAIT from
> entering a sleep state. It does not mean that the UMONITOR instruction is
> disallowed or that the UMONITOR/UMWAIT CPUID enumeration, CPUID.7.0.ECX[5]
> (WAITPKG) is not set. On some processors, this disabling occurs only when a
> microcode update is loaded. Refer to CPUID Enumeration and Architectural MSRs
> for more information.

which is to say, processors affected by a `monitor`/`umonitor` misbehavior _may_
disable the instruction as a result of a microcode update working around the
issue by disabling that instruction. so! consulting CPUID on one
silicon/microcode/motherboard revision may report different extensions from the
same part on a different microcode or motherboard revision.

because microcode packages are tied to specific model/family/steppings of
processors, it's technically possible that silicon supporting a feature could be
present on a processor which is only ever able to load microcode denying that
feature's support. charitably, this might be in the interest of keeping niche
features only enabled in configurations that have been well-tested.
uncharitably, this might be in the interest of funnelling end users towards
different higher-profit products and platforms.

#### on BIOS versions

x86 systems have lots of explicit external initialization that occurs before a
user's disk drives are consulted for the operating system someone actually wants
to run. for more highly-integrated SoC-like x86 processors that the industry has
converged on, this includes a very early stage of the system's firmware (BIOS,
etc) initializing the processor's features beyond some bare minimum sufficient
to execute this bootstrapping.

for BIOSes that include options like "enable {VT-x,VT-d,SVM,AESNI,AVX512,..}",
those settings are made real here. *how* they are made real is not really
documented; this is generally kept between CPU vendors and the platforms
supporting their products. but it must at minimum involve setting some bits that
could take an otherwise-supporting silicon and microcode pair and still refuse
to advertise some feature in CPUID bits.

for the most part this looks a lot like microcode in practice: an uninspectable
blob of code and data installed into the system on a "trust me" basis without so
much as decent patch notes when a change is made.

it is technically possible for features to exist which a BIOS unconditionally
does not enable, let alone allow a user to configure. no examples here, but such
a feature could blip in and out of existence across BIOS versions inadvertently.

motherboard vendors have an opportunity to do their own market segmentation here
as well: "enterprise" features may be disabled on "consumer" motherboards to
drive such interested users towards more "enterprise" platforms and sales
channels.

#### on BIOS/OS configuration

here, finally, is the simplest and most variable way for CPUID bits to vary
across readings of the "same processor": if system A has a feature enabled, and
system B has that feature disabled, it might show as CPUID leaves varying in
otherwise-unexpected ways across different physical copies of the same
motherboard with other versions otherwise all matching.
A, and off 
