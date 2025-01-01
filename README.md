the composite reference for silicon information i've wanted for a long while.

extremely WIP, extremely incomplete. this probably could and maybe should just
be a collection of comprehensive pages on wikipedia, but especially for x86 i
also want tools to look at x86 history through the lens of specific processor
features.

contributions very welcome but exactly what or how to contribute is a mess for now.

this is largely, currently, notes and scraps, but statements and facts should
have citations where possible. i'd like to include relevant reference materials here as well, though PDFs in the repo are not gonna be great.

### x86

x86 CPUID and MSR information is heavily informed by
[InstLatx64](https://github.com/InstLatx64/InstLatx64). interpretations of this
data, as well as tools for querying this data, are under [`x86/`](./x86) as well
as notes on what makes interpretation and general statements... tricky.

CPUID bits and features are basically the easy starting point, but
interpretation of some MSRs is a logical next step.
[https://uops.info/](https://uops.info/) is a great reference for CPU
microarchitecture specifics across time. i'd like to include more product
information here - it should be easy to find exemplar hardware for a feature,
or find which shipping products an instruction sequence would be extra slow on.

[https://www.cpu-world.com/](https://www.cpu-world.com/) has a good breath of relatively high-level product information, but little to the level of detail that would be interesting to folks working against the hardware (either from a software or hardware perspective).

### ARM

there isn't anything on ARM yet. i'd love love love to include broad strokes of
differentiation between ARM cores and SoCs, their peripherals, relevant
firmware, etc. just not something i've gotten to! if this is something you have
good links or references for, please help!

### everything else

g\*d i want to extensively document all the other parts. but i don't have
nearly the time or knowledge! you can help by expanding this list.

this is extremely true for peripherals or bespoke devices. or, for example, the
very poorly-docuemnted IA64 system instructions that seemingly are only used in
IA64 firmware. or system-only instructions in Qualcomm Hexagon processors,
which public manuals only indirectly and seemingly accidentally suggest the
existence of. or fully-undocumented CPUs and architectures.
