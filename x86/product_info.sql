-- information about processors that is more historical in nature.
-- 

create table "vendors" (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  brandstring TEXT NOT NULL
);
insert into vendors (name, brandstring) values ("AMD", "AuthenticAMD");
insert into vendors (name, brandstring) values ("Intel", "GenuineIntel");

create table "uarches" (
  id INTEGER PRIMARY KEY,
  family INTEGER NOT NULL, -- foreign key into `families`
  name TEXT,
  description TEXT
);

create table "families" (
  id INTEGER PRIMARY KEY,
  name TEXT,
  description TEXT,
  -- foreign key into `vendors`
  -- (yes, not great since family_model_info also holds this key..)
  vendor INTEGER NOT NULL
);

insert into families (name, description, vendor) values (
  'Am486', NULL,
  (select id from vendors where name="AMD")
);
insert into families (name, description, vendor) values (
  'K5', NULL,
  (select id from vendors where name="AMD")
);
insert into families (name, description, vendor) values (
  'K6', NULL,
  (select id from vendors where name="AMD")
);
insert into families (name, description, vendor) values (
  'K7', NULL,
  (select id from vendors where name="AMD")
);
insert into families (name, description, vendor) values (
  'K8', NULL,
  (select id from vendors where name="AMD")
);
insert into families (name, description, vendor) values (
  'K10',
  'the marketing name for the the series of parts between K8 and Bulldozer. ' ||
  'the engineering name for the cores here was K9, where K10 was the name for'||
  ' what became Bulldozer. unfortunately it seems at the time that different '||
  'groups in AMD wanted to claim the "next-generation" architecture, and so ' ||
  'K10 itself became a contested name. in the intervening twenty years, K10 ' ||
  'seems to have become the common name in AIDA, cpuid, etc. to quote an old' ||
  ' email? forum post? something? here in 2007, David Kanter from AMD ' ||
  'described: ' || char(10) || char(10) ||
  'Just to clarify terminology:' || char(10) ||
  "Greyhound/Bloodhound i.e. K9 is what is known as barcelona, agena, or whatever. AMD's marketing has tried to rename it to avoid the engineering code-names, but that's fine." || char(10) ||
  char(10) ||
  'The K10 (engineering name) project is what is being referred to as Bulldozer/Sandtiger.' || char(10) ||
  char(10) ||
  'DK' || char(10) || char(10) ||
  'from https://www.realworldtech.com/forum/?threadid=80528&curpostid=80571',
  (select id from vendors where name="AMD")
);
insert into families (name, description, vendor) values (
  'Bobcat', NULL,
  (select id from vendors where name="AMD")
);
insert into families (name, description, vendor) values (
  'Jaguar', NULL,
  (select id from vendors where name="AMD")
);
insert into families (name, description, vendor) values (
  'Bulldozer', NULL,
  (select id from vendors where name="AMD")
);
insert into families (name, description, vendor) values (
  'Zen', NULL,
  (select id from vendors where name="AMD")
);
insert into families (name, description, vendor) values (
  'Zen 3', NULL,
  (select id from vendors where name="AMD")
);

insert into uarches (family, name, description) select
  id, "Am486", NULL from families where name="Am486";
-- first on 1995-11-01
insert into uarches (family, name, description) select
  id, "Am5x86", NULL from families where name="Am486";

insert into uarches (family, name, description) select
  id, "K5", NULL from families where name="K5";

-- HELP! i can't tell what a GeodeLX actually is, architecture-wise. is it an
-- Am5x86? or K5? something else entirely? AMD-branded totally-unrelated-core?
-- it's family 5h, unlike Am5x86, but afaict online sources suggest that it's a
-- rebranded GX2 which was reportedly Am5x86.
-- if you know, i would love a primary source here.
-- failing that, really need to diff cpuid feature sets and make an educated
-- guess
insert into uarches (family, name, description) select
  id, "GeodeLX", NULL from families where name="K5";

insert into uarches (family, name, description) select
  id, "K6", NULL from families where name="K6";
insert into uarches (family, name, description) select
  id, "K6-2", NULL from families where name="K6";
insert into uarches (family, name, description) select
  id, "K6-III", NULL from families where name="K6";
insert into uarches (family, name, description) select
  id, "K6-III+", NULL from families where name="K6";

insert into uarches (family, name, description) select
  id, "K7", NULL from families where name="K7";
insert into uarches (family, name, description) select
  id, "K75", NULL from families where name="K7";
insert into uarches (family, name, description) select
  id, "Morgan", NULL from families where name="K7";
insert into uarches (family, name, description) select
  id, "Palomino", NULL from families where name="K7";
insert into uarches (family, name, description) select
  id, "Spitfire", NULL from families where name="K7";
insert into uarches (family, name, description) select
  id, "Thoroughbred", NULL from families where name="K7";
insert into uarches (family, name, description) select
  id, "Thunderbird", NULL from families where name="K7";
insert into uarches (family, name, description) select
  id, "Barton", NULL from families where name="K7";

insert into uarches (family, name, description) select
  id, "K8", NULL from families where name="K8";
insert into uarches (family, name, description) select
  id, "ClawHammer", NULL from families where name="K8";
insert into uarches (family, name, description) select
  id, "SledgeHammer", NULL from families where name="K8";
insert into uarches (family, name, description) select
  id, "Winchester", NULL from families where name="K8";
insert into uarches (family, name, description) select
  id, "Manchester", NULL from families where name="K8";

-- HELP! there is relatively little to cite about the architecture behind
-- Palermo! it being K8 is an inference from some of these parts supporting
-- AMD64 and AMD64 being introduced in K8. this presumably means that it's not a
-- K7 core with more stuff bolted on? down so bad for a primary source rn fr
insert into uarches (family, name, description) select
  id, "Palermo", NULL from families where name="K8";

-- HELP! this mangles product name and model names pretty bad:
-- family 0xf/model 4/extended model 12 shipped as Sempron, Turion, and Athlon
-- so there's probably some name for the 15/4/12 f/m/ext-m design that i just
-- don't know.
insert into uarches (family, name, description) select
  id, "Venice (2005)", NULL from families where name="K8";
insert into uarches (family, name, description) select
  id, "Santa Rosa", NULL from families where name="K8";
insert into uarches (family, name, description) select
  id, "Windsor", NULL from families where name="K8";
insert into uarches (family, name, description) select
  id, "Orleans", NULL from families where name="K8";
insert into uarches (family, name, description) select
  id, "Brisbane", NULL from families where name="K8";
insert into uarches (family, name, description) select
  id, "Lima", NULL from families where name="K8";

insert into uarches (family, name, description) select
  id, "Bobcat", "reportedly a wholly new design intended for low-power uses"
    from families where name="Bobcat";
insert into uarches (family, name, description) select
  id, "Jaguar", NULL from families where name="Jaguar";
insert into uarches (family, name, description) select
  id, "Cato", NULL from families where name="Jaguar";
insert into uarches (family, name, description) select
  id, "Puma", NULL from families where name="Jaguar";

insert into uarches (family, name, description) select
  id, "K10", NULL from families where name="K10";
insert into uarches (family, name, description) select
  id, "Puma (2008)", NULL from families where name="K10";
insert into uarches (family, name, description) select
  id, "Barcelona", "first AMD64 Opterons!" from families where name="K10";
insert into uarches (family, name, description) select
  id, "Thuban", "first Phenom II!" from families where name="K10";
insert into uarches (family, name, description) select
  id, "Deneb", "more Phenom II, some Athlon X2" from families where name="K10";
insert into uarches (family, name, description) select
  id, "Propus", "particular Phenom II, see https://www.techpowerup.com/98975/amd-athlon-ii-x4-propus-600-quad-core-chips-include-45w-models"
    from families where name="K10";
insert into uarches (family, name, description) select
  id, "Regor", "later Phenom II, some Athlon X2" from families where name="K10";
insert into uarches (family, name, description) select
  id, "Istanbul", "more Opteron" from families where name="K10";
insert into uarches (family, name, description) select
  id, "Magny-Cours", "last of the K10 Opterons" from families where name="K10";

-- HELP! would like better citation on Griffin here..
insert into uarches (family, name, description) select
  id, "Griffin", "last of the K10 Opterons" from families where name="K10";

insert into uarches (family, name, description) select
  id, "Bulldozer", NULL from families where name="Bulldozer";
insert into uarches (family, name, description) select
  id, "Piledriver", NULL from families where name="Bulldozer";
insert into uarches (family, name, description) select
  id, "Steamroller", NULL from families where name="Bulldozer";
insert into uarches (family, name, description) select
  id, "Excavator", NULL from families where name="Bulldozer";

insert into uarches (family, name, description) select
  id, "Zen", NULL from families where name="Zen";
insert into uarches (family, name, description) select
  id, "Zen+", NULL from families where name="Zen";
insert into uarches (family, name, description) select
  id, "Zen 2", NULL from families where name="Zen";
insert into uarches (family, name, description) select
  id, "Zen 3", NULL from families where name="Zen 3";
insert into uarches (family, name, description) select
  id, "Zen 4", NULL from families where name="Zen 3";
insert into uarches (family, name, description) select
  id, "Zen 4c", NULL from families where name="Zen 3";
-- maybe should be a new family in its own right? the rough threshold here is
-- "did issue width increase? probably a new family" so...
insert into uarches (family, name, description) select
  id, "Zen 5", NULL from families where name="Zen 3";


create table "family_model_info" (
  id INTEGER PRIMARY KEY,
  vendor INTEGER NOT NULL,
  family INTEGER,
  ext_family INTEGER,
  model INTEGER,
  ext_model INTEGER,
  uarch INTEGER NOT NULL
);

-- *****************************************************************************
-- ********************** AMD family/model/uarch mappings **********************
-- *****************************************************************************
--
-- upsettingly, sources here are scant. Todd Allen's `cpuid` describes
-- all K6 family processors as K6 uarch, but with more specific synthetic
-- family names. for most purposes i'm concerned about, uarch revisions,
-- such as K6, K6-2, K6-III, should be distinct. similarly, revisions
-- through the Athlon years are very informative, and on and on.
--
-- pages like Wikipedia's `List of AMD K6 processors` are heavily sourced
-- from cpu-world.com/CPUs/*, whose pages currently return text like:
-- > Specifications pages and related web pages were taken down due to
-- > ongoing content scraping.
-- >
-- > The pages will be back online once scraping stops.
--
-- great.
--
-- simultaneously, en.wikichip.org has been down for two weeks so it's
-- not trivial to crosscheck any descriptions there either.
--
-- great.
--
-- so, at a high level this is informed by Todd Allen's descriptions,
-- partially cross-checked by the "CPU Alias" reported by EVEREST or AIDA
-- if a header is available in InstLatx64 dumps, as well as some checking
-- against pages via internet archive.

-- "uarch" and "family" are mushy distinctions. "uarch" tries to hew more
-- closely to an actual description of a physical core that ships in a
-- real product. "family" is a mushier distinction, which might be best
-- described as a "descends-from" relationship. one could of course say
-- that everything descends from the 8086 (or 8080, or 4004, or ..), but
-- this is too broad to be truly informative. so "family" here is a fuzzy
-- line like "more comprehensive change than just adding/expanding
-- caches". practically speaking, for AMD cases, "family" in cpuid
-- reflects this pretty well and tracks with their own branding/marketing
-- of products.
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  4, 0, 3, 0, (select id from uarches where name="Am486")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  4, 0, 7, 0, (select id from uarches where name="Am486")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  4, 0, 8, 0, (select id from uarches where name="Am486")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  4, 0, 9, 0, (select id from uarches where name="Am486")
);

-- https://datasheets.chipdb.org/AMD/486_5x86/19751C.pdf
-- page 56 describes CPUID model/family bits for AMD 5x86
-- processors. this is slightly more precise than `cpuid`.
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  4, 0, 0xe, 0, (select id from uarches where name="Am5x86")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  4, 0, 0xf, 0, (select id from uarches where name="Am5x86")
);
-- cpu-world.com and EVEREST agree F=5/M={0,1} is K5
-- cpuid does not mention these
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  5, 0, 0, 0, (select id from uarches where name="K5")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  5, 0, 1, 0, (select id from uarches where name="K5")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  5, 0, 2, 0, (select id from uarches where name="K5")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  5, 0, 3, 0, (select id from uarches where name="K5")
);
-- there is one GeodeLX in InstLatx64's CPUID collection..
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  5, 0, 0xa, 0, (select id from uarches where name="GeodeLX")
);
-- cpu-world.com, EVEREST, and cpuid all agree these are K6
-- though.
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  5, 0, 6, 0, (select id from uarches where name="K6")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  5, 0, 7, 0, (select id from uarches where name="K6")
);
-- back on our own..
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  5, 0, 8, 0, (select id from uarches where name="K6-2")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  5, 0, 9, 0, (select id from uarches where name="K6-III")
);
-- what about models a-c?
-- "K6-2+" was also family 5/model D, though InstLatx64 has
-- one record of a K6-2+ which can be distinguished only by
-- stepping (4, rather than 0). not bothering with that
-- distiction here yet.
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  5, 0, 0xd, 0, (select id from uarches where name="K6-III+")
);

insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  6, 0, 1, 0, (select id from uarches where name="K7")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  6, 0, 2, 0, (select id from uarches where name="K75")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  6, 0, 3, 0, (select id from uarches where name="Spitfire")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  6, 0, 4, 0, (select id from uarches where name="Thunderbird")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  6, 0, 6, 0, (select id from uarches where name="Palomino")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  6, 0, 7, 0, (select id from uarches where name="Morgan")
);
-- InstLatx86 has a Thoroughbred as stepping 0, Appelbred as
-- stepping 1. no stepping distinguisher here though, yet
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  6, 0, 8, 0, (select id from uarches where name="Thoroughbred")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  6, 0, 10, 0, (select id from uarches where name="Barton")
);
-- reportedly K8 and K7 are very similar, just that K8 also has
-- the minor addition of "x86-64". i've not found much to
-- substantiate this, so [citation needed] as it were.
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0, 0x4, 0, (select id from uarches where name="ClawHammer")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0, 0x5, 0, (select id from uarches where name="SledgeHammer")
);
-- etallen's `cpuid` lists more entries here, but InstLatx64's
-- cpuid collection doesn't have samples to check against, so
-- skipping forward a few..

-- AIDA seemingly reports family 0xf, model 11/ext model 1 and 2 are both
-- Manchester
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0, 0xb, 1, (select id from uarches where name="Manchester")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0, 0xb, 2, (select id from uarches where name="Manchester")
);
-- cpuid leaf 1 eax has `2` in Extended Model ID but model is <0xf?
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0, 0xb, 2, (select id from uarches where name="Manchester")
);
-- notably cpuid leaf 1 eax has a `1` in Extended Model ID for this sample, but
-- the model is 0xc rather than 0xf. by AMD rules the extended model field
-- should be unused..?
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0, 0xc, 1, (select id from uarches where name="Winchester")
);
-- CPUID for AIDA-reported Palermo CPU says model 12 ext model 2...
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0, 0xc, 2, (select id from uarches where name="Palermo")
);
-- AIDA also claims family 0xf model 0xf extended model 1 is Palermo??
-- HELP! would really like more sources here. what's the difference between this
-- and family 0xf, model 0xc/2?
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0, 0xf, 1, (select id from uarches where name="Palermo")
);
-- AIDA says family 0xf model 0xf extended model 2 is Venice (the 2005 one, not
-- the rumored Zen 6 name).
-- HELP! really just want more sources here.
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0, 0xf, 2, (select id from uarches where name="Venice (2005)")
);

insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0, 0x1, 4, (select id from uarches where name="Santa Rosa")
);

insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0, 0x3, 4, (select id from uarches where name="Windsor")
);

insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0, 0xf, 5, (select id from uarches where name="Orleans")
);

insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0, 0xb, 6, (select id from uarches where name="Brisbane")
);

insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0, 0xf, 7, (select id from uarches where name="Lima")
);

-- K10 is a really great example of how "uarch" is reductive,
-- probably should just use the word "model", or swap "family" and
-- "uarch" though that might conflict with what The Rest Of The World
-- means by those things. these processors' *cores* are all largely
-- the same (e.g. "K10"), and the variation between them seems to be
-- more due to process changes (transistor size shrining, changes to
-- whatever the predecessor to the SMU/PSP were). Turbo core was
-- added in the K10 family of parts but that also is not a core
-- change so much as a "microcontroller controlling the core"..
--
-- another problem that's really dramatic in the K10 era is that
-- production parts have the same family/model for different product
-- segments. family 10h model 2 is *not* just "Opteron", but to
-- detect exactly which segment a processor is in you apparently need
-- to consult the brand string to know Opteron, Athlon, etc
--insert into family_model_info (
--  vendor, family, ext_family, model, ext_model, uarch
--) values (
--  (select id from vendors where brandstring="AuthenticAMD"),
--  0xf, 1, 0, 0, (select id from uarches where name="")
--);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 1, 2, 0, (select id from uarches where name="Barcelona")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 1, 4, 0, (select id from uarches where name="Deneb")
);
-- some Propus, at least one Rana too though.
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 1, 5, 0, (select id from uarches where name="Propus")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 1, 6, 0, (select id from uarches where name="Regor")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 1, 8, 0, (select id from uarches where name="Istanbul")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 1, 9, 0, (select id from uarches where name="Magny-Cours")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 1, 10, 0, (select id from uarches where name="Thuban")
);
-- just going by the InstLatx64 CPUID collection and AIDA on this one..
-- HELP! with a list of parts/product codenames this might be a little more
-- clearly sourced..
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 2, 3, 0, (select id from uarches where name="Griffin")
);
-- Llano is reportedly K10 cores glued to a GPU, predating Bobcat. so these are
-- called K10.
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 3, 1, 0, (select id from uarches where name="K10")
);
-- not sure InstLatx64 has samples here.. wikipedia also notes these
-- as "Turion X2 Ultra
--0x11: { "uarch": "Puma (2008)", "family": "K10" },
-- double check A8-3850
--0x12: { "uarch": "Puma (2008)", "family": "K10" },
--0x14: { "uarch": "Bobcat", "family": "Bobcat" },
-- iteration on Bobcat, still all distinct from the construction
-- machine architectures.
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 7, 0, 0, (select id from uarches where name="Jaguar")
);
-- not widely released..
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 7, 2, 0, (select id from uarches where name="Cato")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 7, 8, 0, (select id from uarches where name="Cato")
);
-- distinct from the model 11h Puma! this was more widely shipping.
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 7, 3, 0, (select id from uarches where name="Puma")
);

insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 5, 0, 0, (select id from uarches where name="Bobcat")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 5, 1, 0, (select id from uarches where name="Bobcat")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 5, 2, 0, (select id from uarches where name="Bobcat")
);

-- bulldozer/piledriver/steamroller/excavator
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 6, 0, 0, (select id from uarches where name="Bulldozer")
);
-- different slice of Bulldozer? Interlagos, Zambezi
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 6, 1, 0, (select id from uarches where name="Bulldozer")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 6, 0, 1, (select id from uarches where name="Piledriver")
);
-- double check. FX-8350
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 6, 0, 2, (select id from uarches where name="Piledriver")
);
-- different slice of Piledriver: Abu Dhabi, Vishera
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 6, 2, 0, (select id from uarches where name="Piledriver")
);
-- HELP! information is kind of.. spotty here. these are probably Piledriver,
-- but the only sources i can find are standalone statements like on
-- https://www.tomshardware.com/reviews/a10-6700-a10-6800k-richland-review,3528.html
-- ... it would be nice to directly compare feature bits between Piledriver and
-- other Bulldozer-era cores.
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 6, 3, 1, (select id from uarches where name="Piledriver")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 6, 4, 0, (select id from uarches where name="Steamroller")
);
-- Bald Eagle is described as Steamroller, with an AMD Embedded Processor
-- Roadmap describing it and some smilar-era parts in this article:
-- https://linuxgizmos.com/amd-reveals-arm-and-x86-soc-and-apu-plans/
-- notably, "Steppe Eagle" is described here as Jaguar cores as well
--
-- there's also a "Berlin_00_CPUID" record in InstLatx64's collection, which
-- seems to be a Kaveri APU, so also steamroller
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 6, 0, 3, (select id from uarches where name="Steamroller")
);
-- Godavari appears to be a Kaveri refresh, so also Steamroller
-- https://www.anandtech.com/show/9307/the-kaveri-refresh-godavari-review-testing-amds-a10-7870k
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 6, 8, 3, (select id from uarches where name="Steamroller")
);
-- some Carrizo are family 15h/0+6, others are 15h/5+6
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 6, 0, 6, (select id from uarches where name="Excavator")
);
-- 15h/5+6 is also some Stoney Ridge..
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 6, 5, 6, (select id from uarches where name="Excavator")
);
-- 15h/0+7 (A9-9410) is also Stoney Ridge?
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 6, 0, 7, (select id from uarches where name="Excavator")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 6, 6, 0, (select id from uarches where name="Excavator")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 6, 7, 0, (select id from uarches where name="Excavator")
);

-- double check. A12-9800 etc
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 6, 0xb, 0, (select id from uarches where name="Excavator")
);

-- Beema. Puma cores. this family/model combo also describes some Steppe Eagle
-- parts, so those might be Puma too?
-- talks about Steppe Eagle but not really useful:
-- https://www.cnx-software.com/2014/06/06/amd-introduces-embedded-g-series-steppe-eagle-socs-and-crowned-eagle-cpus/
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 7, 0, 3, (select id from uarches where name="Puma")
);

-- HELP! "Cato", 2019ish maybe OEM part? no idea what this actually is.
-- by date it might be Zen+? Zen 2?
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 7, 6, 2, (select id from uarches where name="Zen")
);

-- Zen and onward. this is a bit funky because AMD describes Zen,
-- Zen_, and Zen 2 together in "Revision Guide for AMD Family 17h
-- Models 00h-0Fh Processors" publication 55449. evidence towards
-- their similarity, i suppose?
-- anyway, `cpuid`'s approach is to encode which specific models were
-- which architecture, probably good enough here too.
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 8, 0, 0, (select id from uarches where name="Zen")
);
-- more Zen (2200G, 2400G, 2500U)
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 8, 1, 1, (select id from uarches where name="Zen")
);
-- HELP! i think Dali has Zen cores, but i don't know for sure!
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 8, 0, 2, (select id from uarches where name="Zen")
);
-- "Zen", these are from "DG02SRTBP4MFA" though.
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 8, 0, 5, (select id from uarches where name="Zen")
);
-- Renoir, Zen 2 APUs But Worse
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 8, 0, 6, (select id from uarches where name="Zen")
);
-- Rome, but also Castle Peak. Zen 2.
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 8, 1, 3, (select id from uarches where name="Zen")
);
-- Van Gogh is some kinda APU situation, Zen 2 cores, so called "Zen" here.
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 8, 0, 9, (select id from uarches where name="Zen")
);
-- Van Gogh is also 17h/1+9
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 8, 1, 9, (select id from uarches where name="Zen")
);
-- Zen+ (InstLatx64 has 2990WX/2950X samples here)
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 8, 8, 0, (select id from uarches where name="Zen")
);
-- HELP! Picasso Zen+ APUs. not Zen 2!?
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 8, 8, 1, (select id from uarches where name="Zen")
);
-- Lucienne, FP2 Zen 2 APUs
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 8, 8, 6, (select id from uarches where name="Zen")
);
-- Mendocino, Zen 2 APUs
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 8, 0, 0xa, (select id from uarches where name="Zen")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 8, 1, 0, (select id from uarches where name="Zen")
);
-- the 4700S and 4800S are weird. they are reportedly Zen 2, but their
-- family/model sems pretty arbitrary? anyway, 4700S first, 4800S next
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 8, 7, 4, (select id from uarches where name="Zen")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 8, 4, 8, (select id from uarches where name="Zen")
);
-- Matisse, Zen 2
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 8, 1, 7, (select id from uarches where name="Zen")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 8, 2, 0, (select id from uarches where name="Zen")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 8, 3, 0, (select id from uarches where name="Zen 2")
);
-- other fam 17h models not mentioned above are... probably Zen 2?
--0x17: { "uarch": "Zen 2", "family": "Zen" },

-- mostly by vibes: Zen 3 seems distinct enough from Zen/Zen 2 to be
-- a new "family".
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xa, 0, 0, (select id from uarches where name="Zen 3")
);
-- Cezanne, seemingly
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xa, 0, 5, (select id from uarches where name="Zen 3")
);
-- Vermeer?
-- HELP! weird that model 1+0 below is Zen 4? is something wrong here? really
-- should use the codenames here with part references.
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xa, 1, 2, (select id from uarches where name="Zen 3")
);
-- though Zen 4 was a refresh on Zen 3 rather than substantially
-- different
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xa, 1, 0, (select id from uarches where name="Zen 4")
);
-- HELP! Genoa? why is Genoa 1+1 but Vermeer is 1+2 aka Zen 3????
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xa, 1, 1, (select id from uarches where name="Zen 4")
);
-- several Raphael samples here in InstLatx64..
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xa, 1, 6, (select id from uarches where name="Zen 4")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xa, 2, 0, (select id from uarches where name="Zen 3")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xa, 3, 0, (select id from uarches where name="Zen 3")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xa, 4, 0, (select id from uarches where name="Zen 3")
);
-- family 19h/model 4 ext model 4 is Rembrandt, which is "Zen 3+" cores.
-- see: https://www.anandtech.com/show/17276/amd-ryzen-9-6900hs-rembrandt-benchmark-zen3-plus-scaling
-- changes from Zen 3 are all around power management
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xa, 4, 4, (select id from uarches where name="Zen 3")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xa, 5, 0, (select id from uarches where name="Zen 3")
);
-- HELP! Phoenix?
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xa, 5, 7, (select id from uarches where name="Zen 4")
);
-- HELP! MORE Phoenix? Ryzen 9 7940H??
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xa, 4, 7, (select id from uarches where name="Zen 4")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xa, 6, 0, (select id from uarches where name="Zen 4")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xa, 7, 0, (select id from uarches where name="Zen 4")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xa, 8, 0, (select id from uarches where name="Zen 4")
);
-- HELP! Storm Peak?
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xa, 8, 1, (select id from uarches where name="Zen 4")
);
-- HELP! Phoenix 2?
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xa, 8, 7, (select id from uarches where name="Zen 4")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xa, 9, 0, (select id from uarches where name="Zen 4")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xa, 10, 0, (select id from uarches where name="Zen 4c")
);


-- at least Ryzen 9 7940H w/ Radeon 780M?
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xa, 11, 0, (select id from uarches where name="Zen 4")
);
-- at least Ryzen 9 7940H
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xa, 12, 0, (select id from uarches where name="Zen 4")
);
-- at least Ryzen 7 8700G
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xa, 13, 0, (select id from uarches where name="Zen 4")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xa, 15, 0, (select id from uarches where name="Zen 4")
);

-- allegedly a "ground up redesign" of zen 3, i don't know how
-- similar or different this is from zen 3/4 yet though.
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xb, 0, 0, (select id from uarches where name="Zen 5")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xb, 1, 0, (select id from uarches where name="Zen 5")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xb, 2, 0, (select id from uarches where name="Zen 5")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xb, 3, 0, (select id from uarches where name="Zen 5")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xb, 4, 0, (select id from uarches where name="Zen 5")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xb, 5, 0, (select id from uarches where name="Zen 5")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xb, 6, 0, (select id from uarches where name="Zen 5")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xb, 7, 0, (select id from uarches where name="Zen 5")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="AuthenticAMD"),
  0xf, 0xb, 4, 4, (select id from uarches where name="Zen 5")
);

-- currently, this is really "processors" or "cpus", but it'd be nice to expand
-- this to other non-processor electronics, so take the more generic name now...
create table "devices" (
  id INTEGER PRIMARY KEY,
  vendor INTEGER NOT NULL,
  -- uarch is probably a poor name... in the context of CPUs, "uarch" is a
  -- decent shorthand for "other places you'd expect the same reference manual
  -- and features to be as applicable, mostly, probably". in the context of,
  -- say, NICs this might be "BCM57504"?
  uarch INTEGER NOT NULL,
  -- is this device an actual shipping product? or is ES/QS that there are
  -- nonetheless measurements for?
  preprod BOOLEAN,
  -- is this device one that is only in custom OEM equipment? note that OEM and
  -- ES/QS are independent - there are Amazon OEM CPUs on ebay, but they might
  -- be as production as anything else you can buy. arguably one might call
  -- Apple Silicon "OEM" in this regard too..?
  oem BOOLEAN,
  -- is this device one that you would be able to easily buy and operate?
  -- or, another way, is it likely a user of this device a company with
  -- procurement and maintenance teams. if this is true, it's probably not OEM,
  -- but they're not mutually exclusive - Apple Silicon and Graviton are both
  -- solid contenders for "true on both counts".
  generally_available BOOLEAN,
  description TEXT
);
create table "features" (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  value INTEGER
);

-- *****************************************************************************
-- ************************ INTEL MODEL AND FAMILY INFO ************************
-- *****************************************************************************
--

insert into families (name, description, vendor) values ('486', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('P5', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('P6', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('NetBurst', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Core', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Penryn', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Nehalem', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Westmere', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Sandy Bridge', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Ivy Bridge', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Haswell', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Broadwell', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Skylake', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Cascade Lake', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Cooper Lake', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Kaby Lake', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Coffee Lake', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Whiskey Lake', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Amber Lake', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Palm Cove', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Coffee Lake', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Comet Lake', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Sunny Cove', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Willow Cove', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Cypress Cove', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Golden Cove', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Raptor Cove', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Redwood Cove', NULL,
  (select id from vendors where name="Intel")
);
-- HELP: Panther Cove would be... here? cpuid says MSR_CPUID_table momentarily
-- described this as family 15, ext-family 4

-- finally, the low-power *mont cores, starting with .... Bonnell (yes yes, not
  -- a mont.)
insert into families (name, description, vendor) values ('Bonnell', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Saltwell', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Silvermont', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Airmont', NULL,
  (select id from vendors where name="Intel")
);
-- absent better classification, KNL was kinda Airmont but also AVX512 etc.
-- so it's separated out to not muddy up the classifications.
insert into families (name, description, vendor) values ('AirmontKNL', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Goldmont', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Goldmont+', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Tremont', NULL,
  (select id from vendors where name="Intel")
);
insert into families (name, description, vendor) values ('Gracemont', NULL,
  (select id from vendors where name="Intel")
);
-- Meteor Lake E-cores, at least
insert into families (name, description, vendor) values ('Crestmont', NULL,
  (select id from vendors where name="Intel")
);
-- Lunar Lake E-cores
insert into families (name, description, vendor) values ('Skymont', NULL,
  (select id from vendors where name="Intel")
);

-- HELP: was Lakemont really the name of cores used in Quark?
insert into families (name, description, vendor) values ('Lakemont', NULL,
  (select id from vendors where name="Intel")
);

-- continuing the farce from backwards AMD tables: map 486 through NetBurst to
-- "families" of the same name.
insert into uarches (family, name, description) select
  id, "486", NULL from families where name="486";
insert into uarches (family, name, description) select
  id, "P5", NULL from families where name="P5";
insert into uarches (family, name, description) select
  id, "P54C", NULL from families where name="P5";
insert into uarches (family, name, description) select
  id, "P24T", NULL from families where name="P5";
insert into uarches (family, name, description) select
  id, "P55C", NULL from families where name="P5";
-- HELP: accurate categorization?
insert into uarches (family, name, description) select
  id, "Tillamook", NULL from families where name="P5";
-- HELP: need better citation, but it seems like "Lakemont" describes the cores
-- used in Quark products?
insert into uarches (family, name, description) select
  id, "Clanton", NULL from families where name="Lakemont";
insert into uarches (family, name, description) select
  id, "P6", NULL from families where name="P6";
insert into uarches (family, name, description) select
  id, "P2OD", NULL from families where name="P6";
insert into uarches (family, name, description) select
  id, "Katmai", NULL from families where name="P6";
insert into uarches (family, name, description) select
  id, "Coppermine", NULL from families where name="P6";
-- HELP: mirror and notes:
-- https://www.anandtech.com/show/1083/2
-- very similar to P4 in some respects, apparently.. maybe not call this "P6"?
insert into uarches (family, name, description) select
  id, "Banias", NULL from families where name="P6";
insert into uarches (family, name, description) select
  id, "Cascades", NULL from families where name="P6";
insert into uarches (family, name, description) select
  id, "Tualatin", NULL from families where name="P6";
insert into uarches (family, name, description) select
  id, "Dothan", NULL from families where name="P6";
insert into uarches (family, name, description) select
  id, "Tolapai", NULL from families where name="P6";
-- HELP: at least according to wikipedia (lol) this is a follow-on rev of Banias
-- with SSE3, NX, other changes. and was used in Core Solo and Core Duo? but not
-- conroe. lol ??
insert into uarches (family, name, description) select
  id, "Yonah", NULL from families where name="P6";
insert into uarches (family, name, description) select
  id, "NetBurst", NULL from families where name="NetBurst";
insert into uarches (family, name, description) select
  id, "Willamette", NULL from families where name="NetBurst";
insert into uarches (family, name, description) select
  id, "Northwood", NULL from families where name="NetBurst";
insert into uarches (family, name, description) select
  id, "Prescott", NULL from families where name="NetBurst";
insert into uarches (family, name, description) select
  id, "Cedar Mill", NULL from families where name="NetBurst";
-- INTEL HAD CODENAMES FOR EACH COMBINATION OF SEGMENT AND CORE COUNT??
insert into uarches (family, name, description) select
  id, "Merom", NULL from families where name="Core";
insert into uarches (family, name, description) select
  id, "Conroe", NULL from families where name="Core";
insert into uarches (family, name, description) select
  id, "Allendale", NULL from families where name="Core";
insert into uarches (family, name, description) select
  id, "Kentsfields", NULL from families where name="Core";
insert into uarches (family, name, description) select
  id, "Clovertown", NULL from families where name="Core";
insert into uarches (family, name, description) select
  id, "Woodcrest", NULL from families where name="Core";
insert into uarches (family, name, description) select
  id, "Tigerton", NULL from families where name="Core";
-- PENRYN IS WORSE: THE 45NM SHRINK OF CORE IS NAMED PENRYN BUT SO ARE SOME
-- SPECIFIC CPUS USING PENRYN CORES.
-- i thought i was going crazy until i tripped over
-- https://www.theregister.com/2007/09/19/idf_intel_penryn_decoder/
-- which includes:
-- > Yes, it's the same name as the generic 45nm architecture, but that hasn't
-- > stopped Intel codenaming its upcoming mobile Core 2 Duos and Core 2
-- > Extremes Penryn too. All due in Q1 2008, they're dual-core parts with 3MB
-- > or 6MB of L2 cache. Expect to see a 2.8GHz Core 2 Extreme X9000 at launch,
-- > along with four 'Santa Rosa refresh' Core 2 Duos: the T8100, T8300, T9300
-- > and T9500, clocked at 2.1GHz, 2.4GHz, 2.5GHz and 2.6GHz, respectively.
--
-- TODO: separtely, seems like etallen's FAMILY.NOTES incorrectly lists 2-core
-- mobile Penryn-based parts as Merom-3M, when it should be Penryn-3M.
insert into uarches (family, name, description) select
  id, "Penryn", NULL from families where name="Penryn";
insert into uarches (family, name, description) select
  id, "Wolfdale", NULL from families where name="Penryn";
insert into uarches (family, name, description) select
  id, "Yorkfield", NULL from families where name="Penryn";
insert into uarches (family, name, description) select
  id, "Harpertown", NULL from families where name="Penryn";
insert into uarches (family, name, description) select
  id, "Dunnington", NULL from families where name="Penryn";
-- more variants for Nehalem...
insert into uarches (family, name, description) select
  id, "Clarksfield", NULL from families where name="Nehalem";
insert into uarches (family, name, description) select
  id, "Lynnfield", NULL from families where name="Nehalem";
insert into uarches (family, name, description) select
  id, "Jasper Forest", NULL from families where name="Nehalem";
insert into uarches (family, name, description) select
  id, "Bloomfield", NULL from families where name="Nehalem";
insert into uarches (family, name, description) select
  id, "Gainestown", NULL from families where name="Nehalem";
insert into uarches (family, name, description) select
  id, "Beckton", NULL from families where name="Nehalem";
-- and more for Westmere. almost done...
insert into uarches (family, name, description) select
  id, "Arrandale", NULL from families where name="Westmere";
insert into uarches (family, name, description) select
  id, "Clarkdale", NULL from families where name="Westmere";
insert into uarches (family, name, description) select
  id, "Gulftown", NULL from families where name="Westmere";
-- HELP: there's Westmere-EP and Westmere-EX. rounding to just "Westmere" here..
insert into uarches (family, name, description) select
  id, "Westmere", NULL from families where name="Westmere";
-- finally Sandy Bridge and onward gets simple-ish.
insert into uarches (family, name, description) select
  id, "Sandy Bridge", NULL from families where name="Sandy Bridge";
insert into uarches (family, name, description) select
  id, "Ivy Bridge", NULL from families where name="Ivy Bridge";
insert into uarches (family, name, description) select
  id, "Haswell", NULL from families where name="Haswell";
insert into uarches (family, name, description) select
  id, "Broadwell", NULL from families where name="Broadwell";
insert into uarches (family, name, description) select
  id, "Skylake", NULL from families where name="Skylake";
insert into uarches (family, name, description) select
  id, "Cascade Lake", NULL from families where name="Cascade Lake";
insert into uarches (family, name, description) select
  id, "Cooper Lake", NULL from families where name="Cooper Lake";
insert into uarches (family, name, description) select
  id, "Kaby Lake", NULL from families where name="Kaby Lake";
insert into uarches (family, name, description) select
  id, "Coffee Lake", NULL from families where name="Coffee Lake";
insert into uarches (family, name, description) select
  id, "Whiskey Lake", NULL from families where name="Whiskey Lake";
insert into uarches (family, name, description) select
  id, "Amber Lake", NULL from families where name="Amber Lake";
insert into uarches (family, name, description) select
  id, "Coffee Lake", NULL from families where name="Coffee Lake";
insert into uarches (family, name, description) select
  id, "Comet Lake", NULL from families where name="Comet Lake";
insert into uarches (family, name, description) select
  id, "Cannon Lake", NULL from families where name="Palm Cove";
-- uh oh, product name and architectures start diverging again!
insert into uarches (family, name, description) select
  id, "Ice Lake", NULL from families where name="Sunny Cove";
insert into uarches (family, name, description) select
  id, "Tiger Lake", NULL from families where name="Willow Cove";
insert into uarches (family, name, description) select
  id, "Rocket Lake", NULL from families where name="Cypress Cove";
-- HELP! how to include Alder Lake and onward with E-cores and P-cores?
-- HELP! just going with P-cores for now
insert into uarches (family, name, description) select
  id, "Alder Lake", NULL from families where name="Golden Cove";
insert into uarches (family, name, description) select
  id, "Sapphire Rapids", NULL from families where name="Golden Cove";
-- HELP! document the model/uarch funkiness here
insert into uarches (family, name, description) select
  id, "Raptor Lake", NULL from families where name="Raptor Cove";
-- HELP! there's not even a wiki page here! gotta go add that!
-- https://chipsandcheese.com/p/intels-redwood-cove-baby-steps-are-still-steps
insert into uarches (family, name, description) select
  id, "Raptor Lake", NULL from families where name="Raptor Cove";
-- the server part with Raptor Cove only?
insert into uarches (family, name, description) select
  id, "Emerald Rapids", NULL from families where name="Raptor Cove";
insert into uarches (family, name, description) select
  id, "Meteor Lake", NULL from families where name="Redwood Cove";

-- and then Atom...
-- HELP! not being precise about the product codenames for Atom yet
-- might need to? might not? depends on CPUID..
insert into uarches (family, name, description) select
  id, "Bonnell", NULL from families where name="Bonnell";
insert into uarches (family, name, description) select
  id, "Bonnell 2", NULL from families where name="Bonnell 2";
insert into uarches (family, name, description) select
  id, "Saltwell", NULL from families where name="Saltwell";
insert into uarches (family, name, description) select
  id, "Silvermont", NULL from families where name="Silvermont";
insert into uarches (family, name, description) select
  id, "Airmont", NULL from families where name="Airmont";
insert into uarches (family, name, description) select
  id, "Knights Landing", NULL from families where name="Airmont";
insert into uarches (family, name, description) select
  id, "Goldmont", NULL from families where name="Goldmont";
insert into uarches (family, name, description) select
  id, "Goldmont+", NULL from families where name="Goldmont+";
insert into uarches (family, name, description) select
  id, "Tremont", NULL from families where name="Tremont";
insert into uarches (family, name, description) select
  id, "Jasper Lake", NULL from families where name="Tremont";
insert into uarches (family, name, description) select
  id, "Elkhart Lake", NULL from families where name="Tremont";
-- mix of Tremont and Sunny Cove cores. picking Sunny Cove for "max features".
-- if they set CPUID bits to lowest common denominator, i suppose that means
-- this might claim Sunny Cove cores do not support features other Sunny
-- Cove-only processors would.
insert into uarches (family, name, description) select
  id, "Lakefield", NULL from families where name="Sunny Cove";
insert into uarches (family, name, description) select
  id, "Gracemont", NULL from families where name="Gracemont";
insert into uarches (family, name, description) select
  id, "Crestmont", NULL from families where name="Crestmont";

-- now for family/model info..
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  4, 0, 8, 0, (select id from uarches where name="486")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  5, 0, 1, 0, (select id from uarches where name="P5")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  5, 0, 2, 0, (select id from uarches where name="P54C")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  5, 0, 3, 0, (select id from uarches where name="P24T")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  5, 0, 4, 0, (select id from uarches where name="P55C")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  5, 0, 7, 0, (select id from uarches where name="P54C")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  5, 0, 8, 0, (select id from uarches where name="Tillamook")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  5, 0, 9, 0, (select id from uarches where name="Clanton")
);
-- some more family 5 are skipped..
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 1, 0, (select id from uarches where name="P6")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 3, 0, (select id from uarches where name="P2OD")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 5, 0, (select id from uarches where name="P6")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 6, 0, (select id from uarches where name="P6")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 7, 0, (select id from uarches where name="Katmai")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 8, 0, (select id from uarches where name="Coppermine")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 9, 0, (select id from uarches where name="Banias")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 0xa, 0, (select id from uarches where name="Cascades")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 0xb, 0, (select id from uarches where name="Tualatin")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 0xd, 0, (select id from uarches where name="Dothan")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 0xe, 0, (select id from uarches where name="Yonah")
);

-- HELP: according to wikipedia (so, better citation please)
-- and/or this IA Ars link:
-- https://arstechnica.com/gadgets/2007/08/intel-confirms-details-of-tolapai-a-soc-embedded-processor/
-- it's seemingly a revised Dothan..
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 5, 1, (select id from uarches where name="Tolapai")
);


-- lots of Netburst..
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  15, 0, 0, 0, (select id from uarches where name="Willamette")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  15, 0, 1, 0, (select id from uarches where name="Willamette")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  15, 0, 2, 0, (select id from uarches where name="Northwood")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  15, 0, 3, 0, (select id from uarches where name="Prescott")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  15, 0, 4, 0, (select id from uarches where name="Prescott")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  15, 0, 6, 0, (select id from uarches where name="Cedar Mill")
);
----------
-- `cpuid` calls these both Merom, but one of these should probably be Conroe..?
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 0xf, 0, (select id from uarches where name="Merom")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 6, 1, (select id from uarches where name="Merom")
);

insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 7, 1, (select id from uarches where name="Penryn")
);
-- HELP what's the difference??
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 13, 1, (select id from uarches where name="Penryn")
);

insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 10, 1, (select id from uarches where name="Bloomfield")
);
-- HELP: brand/processor codename depends on segment and stepping. this is
-- actually a mix of Jasper Forest, Lynnfield, Clarksfield...
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 14, 1, (select id from uarches where name="Lynnfield")
);
-- HELP: cpuid reports this as Havendale/Auburndale, dunno if InstLatx64 has any
-- processors of this type, presumably these are fundamentally Nehalem cores
-- too, so use Lynnfield as the nexy closest approximation
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 15, 1, (select id from uarches where name="Lynnfield")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 14, 2, (select id from uarches where name="Beckton")
);

insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 12, 1, (select id from uarches where name="Bonnell")
);

insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 5, 2, (select id from uarches where name="Westmere")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 12, 2, (select id from uarches where name="Westmere")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 15, 2, (select id from uarches where name="Westmere")
);

insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 6, 2, (select id from uarches where name="Bonnell")
);

insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 7, 2, (select id from uarches where name="Saltwell")
);
-- HELP family/ext family differences again...
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 5, 3, (select id from uarches where name="Saltwell")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 6, 3, (select id from uarches where name="Saltwell")
);

insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 10, 2, (select id from uarches where name="Sandy Bridge")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 13, 2, (select id from uarches where name="Sandy Bridge")
);

insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 7, 3, (select id from uarches where name="Silvermont")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 10, 4, (select id from uarches where name="Silvermont")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 13, 4, (select id from uarches where name="Silvermont")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 10, 5, (select id from uarches where name="Silvermont")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 13, 5, (select id from uarches where name="Silvermont")
);

insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 10, 2, (select id from uarches where name="Sandy Bridge")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 13, 2, (select id from uarches where name="Sandy Bridge")
);

insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 10, 3, (select id from uarches where name="Ivy Bridge")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 14, 3, (select id from uarches where name="Ivy Bridge")
);

insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 12, 3, (select id from uarches where name="Haswell")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 15, 3, (select id from uarches where name="Haswell")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 5, 4, (select id from uarches where name="Haswell")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 6, 4, (select id from uarches where name="Haswell")
);

insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 13, 3, (select id from uarches where name="Broadwell")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 7, 4, (select id from uarches where name="Broadwell")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 15, 4, (select id from uarches where name="Broadwell")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 6, 5, (select id from uarches where name="Broadwell")
);

insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 12, 4, (select id from uarches where name="Airmont")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 14, 6, (select id from uarches where name="Airmont")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 5, 7, (select id from uarches where name="Airmont")
);

insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 7, 5, (select id from uarches where name="Airmont")
);

insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 14, 4, (select id from uarches where name="Skylake")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 5, 5, (select id from uarches where name="Skylake")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 14, 5, (select id from uarches where name="Skylake")
);

insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 12, 9, (select id from uarches where name="Jasper Lake")
);

-- HELP: just following AIDA and cpuid here..
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 6, 9, (select id from uarches where name="Elkhart Lake")
);

-- HELP: so.. Lakefield is an early heterogeneous part? the first?
-- https://www.anandtech.com/show/15877/intel-hybrid-cpu-lakefield-all-you-need-to-know
-- seemingly Sunny Cove + some number of Tremont. bias towards Sunny Cove for
-- maximum feature bits..
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 10, 8, (select id from uarches where name="Lakefield")
);

-- Kaby Lake and many related are specifically non-zero steppings on Skylake..?
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 14, 4, (select id from uarches where name="Kaby Lake")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 14, 5, (select id from uarches where name="Kaby Lake")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 14, 8, (select id from uarches where name="Kaby Lake")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 14, 9, (select id from uarches where name="Kaby Lake")
);

-- etallen makes a compelling argument that Whiskey Lake, Amber Lake, and Comet
-- Lake are uninteresting branding names that are fundamentally equivalent to
-- Kaby Lake. from a CPU core perspective anyway. the PCH between these vary
-- somewhat more..
-- HELP: useful to distinguish the PCH here? or no? maybe???
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 9, 5, (select id from uarches where name="Kaby Lake")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 10, 5, (select id from uarches where name="Kaby Lake")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 10, 6, (select id from uarches where name="Kaby Lake")
);

-- See above about Skylake and marketing names. "Comet Lake" here in
-- anticipation of related but non-CPU feature changes..
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 5, 10, (select id from uarches where name="Comet Lake")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 6, 10, (select id from uarches where name="Comet Lake")
);

insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 12, 5, (select id from uarches where name="Goldmont")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 15, 5, (select id from uarches where name="Goldmont")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 10, 7, (select id from uarches where name="Goldmont+")
);

insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 6, 6, (select id from uarches where name="Cannon Lake")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 7, 6, (select id from uarches where name="Cannon Lake")
);

insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 10, 6, (select id from uarches where name="Ice Lake")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 12, 6, (select id from uarches where name="Ice Lake")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 13, 7, (select id from uarches where name="Ice Lake")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 14, 7, (select id from uarches where name="Ice Lake")
);

insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 12, 8, (select id from uarches where name="Tiger Lake")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 13, 8, (select id from uarches where name="Tiger Lake")
);

-- Golden Cove (incl Sapphire Rapids)
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 0xf, 8, (select id from uarches where name="Sapphire Rapids")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 5, 9, (select id from uarches where name="Sapphire Rapids")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 7, 9, (select id from uarches where name="Sapphire Rapids")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 10, 9, (select id from uarches where name="Alder Lake")
);

insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 7, 11, (select id from uarches where name="Raptor Lake")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 10, 11, (select id from uarches where name="Raptor Lake")
);
-- HELP: InstLatx64 calls this "Alder Lake-N", but cpuid calls 
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 14, 11, (select id from uarches where name="Raptor Lake")
);
-- HELP: cpuid says this comes from MSR_CPUID_table, not sure what the
-- difference here is vs other family/models.. InstLatx64 (AIDA) claims this is
-- "Alder Lake-N".
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 15, 11, (select id from uarches where name="Raptor Lake")
);

-- Cypress Cove. similar to Sunny Cove but on 14nm instead of 10nm.
-- HELP: archive
-- https://www.anandtech.com/show/16495/intel-rocket-lake-14nm-review-11900k-11700k-11600k/2
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 7, 10, (select id from uarches where name="Rocket Lake")
);

-- Meteor Lake, there are a few samples here in InstLatX64
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 10, 10, (select id from uarches where name="Meteor Lake")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 11, 10, (select id from uarches where name="Meteor Lake")
);
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 12, 10, (select id from uarches where name="Meteor Lake")
);

-- cpuid describes this as Panther Lake, not sure what's going on here yet.
insert into family_model_info (
  vendor, family, ext_family, model, ext_model, uarch
) values (
  (select id from vendors where brandstring="GenuineIntel"),
  6, 0, 15, 12, (select id from uarches where name="Emerald Rapids")
);
