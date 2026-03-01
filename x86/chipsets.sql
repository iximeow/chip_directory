-- so, in the *old days* chipsets were many disparate chips on a mainboard that
-- a CPU was connected to in some manner (i.e. "a socket", or "a soldered QFP").
-- over time, different functions have consolidated together. what was once
-- external cache management moved on-CPU, the "high bandwidth" stuff like
-- memory, AGP, PCIe, ended up in "the north bridge", all the other
-- miscellaneous I/O got rolled up into "the south bridge", and then even these
-- have moved into the CPU package depending on where and when you look.
--
-- documentation availability here is scattered, trends towards less public,
-- more NDA-encumbered, and generally what seems like a "just trust us, the
-- vendor" philosophy. it is quite unfortunate.
--
-- for what *is* available, i'm organizing it roughly into groups of hardware
-- you'd find together in functional systems in support of a particular CPU
-- vendor. as an example, an i7-3770K may have been found in an ASUS P8Z77-V LX
-- motherboard with an Intel Z77 chipset. there will be a "Z77" chipset for the
-- consumer Intel Sandy Bridge and Ivy Bridge parts. this in turn will include a
-- Platform Controller Hub document for the Intel 7 Series/C216 Chipset Family
-- Platform Controller Hub and an Uncore document for the Intel Software
-- Developer's Manual noting "MSRS IN THE INTEL® PROCESSOR FAMILY BASED ON SANDY
-- BRIDGE MICROARCHITECTURE" as specifically relevant content. missing here are
-- any documents that would have been useful for BIOS implementation or
-- analysis; what MSRs or configuration interfaces did an Intel BIOS use to
-- enable or disable VT-x, for example? this is likely documented in NDA'd and
-- unavailable material, and is shrimply a blind spot we must live with. awful.
create table "chipsets" (
  id INTEGER PRIMARY KEY,
  codename TEXT,
  human_name TEXT,
  description TEXT,
  segment INTEGER NOT NULL,
  vendor INTEGER NOT NULL,
  -- key into doc_items
  doc_item INTEGER
);

alter table families add column "chipset";
alter table uarches add column "chipset";

-- especially for older (Penryn-era) product intersections,
-- https://www.supermicro.com/products/motherboard/archive/ is a great reference

-- see https://www.intel.com/content/www/us/en/ark/products/series/229717/intel-700-series-desktop-chipsets.html
insert into "chipsets" (
  codename, human_name, description, segment, vendor
) values (
  "",
  "Intel 800 Series",
  "Intel 800 Series Chipset Family Platform Controller Hub (H810, B860, Q870, W880, Z890)",
  "",
  1,
  (select id from vendors where name="Intel")
);

update families set chipset=(
  select id from chipsets where human_name="Intel 800 Series"
) where name in ("Arrow Lake"); -- and others?

-- see https://www.intel.com/content/www/us/en/ark/products/series/229717/intel-700-series-desktop-chipsets.html
insert into "chipsets" (
  codename, human_name, description, segment, vendor
) values (
  "",
  "Intel 700 Series",
  "Intel 700 Series Chipset Family Platform Controller Hub (W790, B760, H770, Z790)",
  "",
  1,
  (select id from vendors where name="Intel")
);

-- no public datasheets i can find.
insert into "chipsets" (
  codename, human_name, description, segment, vendor
) values (
  "Emmitsburg",
  "Intel C74x",
  "Chipsets used across C741E and others?",
  1,
  (select id from vendors where name="Intel")
);

-- don't link C74x specifically to sapphire rapids (yet?) because the 700-series
-- update families set chipset=(
--   select id from chipsets where human_name="Intel C74x"
-- ) where name in ("Emerald Rapids", "Sapphire Rapids");
update families set chipset=(
  select id from chipsets where human_name="Intel 700 Series"
) where name in ("Emerald Rapids", "Sapphire Rapids");

insert into "chipsets" (
  codename, human_name, description, segment, vendor
) values (
  "",
  "Intel C621A",
  "Chipsets used for 3rd Generation Intel Xeon Scalable Processor. At least C621A, maybe others?",
  1,
  (select id from vendors where name="Intel")
);

-- hard to find intel documents to cite here...
update families set chipset=(
  select id from chipsets where human_name="Intel C621A"
) where name in ("Ice Lake");

-- the wider platform name for products with Skylake-SP processors, Lewisburg PCHs, etc, is "Purley":
-- https://www.intel.com/content/www/us/en/products/platforms/details/purley.html
insert into "chipsets" (
  codename, human_name, description, segment, vendor
) values (
  "Lewisburg",
  "Intel C62x",
  "Chipset family spanning C621, C622, C624, C625, C626, C627, C628",
  1,
  (select id from vendors where name="Intel")
);

-- Lewisburg and C620-specific documents apply only to the server parts, not client/mobile..
update families set chipset=(
  select id from chipsets where human_name="Intel C62x"
) where name in ("Skylake", "Cascade Lake");

insert into "chipsets" (
  codename, human_name, description, segment, vendor
) values (
  "Wellsburg",
  "Intel C61x",
  "Chipset family spanning C612, X99",
  1,
  (select id from vendors where name="Intel")
);

-- Wesllburg/X99/C610 only apply to enthusiast/extreme and xeon Haswell/Broadwell...
update families set chipset=(
  select id from chipsets where human_name="Intel C61x"
) where name in ("Haswell", "Broadwell");

insert into "chipsets" (
  codename, human_name, description, segment, vendor
) values (
  "Panther Point",
  "Intel 7x/Intel C216",
  "Chipset family supporting the Intel 7x (non-server) and C216 (server) chipsets",
  1,
  (select id from vendors where name="Intel")
);

update families set chipset=(
  select id from chipsets where human_name="Intel 7x/Intel C216"
) where name in ("Ivy Bridge", "Sandy Bridge");

insert into "chipsets" (
  codename, human_name, description, segment, vendor
) values (
  "Cougar Point",
  "Intel 6x/Intel C20x",
  "Chipset family supporting the Intel 5x (non-server) and C20x (server) chipsets",
  1,
  (select id from vendors where name="Intel")
);

-- would be Sandy Bridge, the 7x family supports Sandy Bridge and more though.
-- see HELP about the processor/chipset relationships...

insert into "chipsets" (
  codename, human_name, description, segment, vendor
) values (
  "Ibex Point",
  "Intel 5x/Intel 34xx",
  "Chipset family supporting the Intel 5x (non-server) and 34xx (server) chipsets",
  1,
  (select id from vendors where name="Intel")
);

-- there are a smattering of chipsets here, which support different product
-- lines. see
-- https://www.intel.com/content/www/us/en/ark/products/codename/29960/products-formerly-ibex-peak.html
--
-- in total, this covers Clarksfield, Lynnfield, Arrandale, Clarkdale,
-- Bloomfield, Gainestown (aka Nehalem EP, like X5550), Jasper Forest
--
-- it does NOT include Beckton aka Nehalem-EX and Westmere-EX.
update uarches set chipset=(
  select id from chipsets where human_name="Intel 5x/Intel 34xx"
) where name in (
  -- 
  "Lynnfield",
  "Clarkfield",
  "Arrandale",
  "Clarkdale",
  "Bloomfield",
  -- X58 chipset, CPUs like i7-990X, W3690.
  "Gulftown",
  -- 3420 chipset, CPUs like Xeon EC5509
  "Jasper Forest"
);

insert into "chipsets" (
  codename, human_name, description, segment, vendor
) values (
  "Blackford",
  "Intel® 5000P/5000V/5000Z Chipset Memory Controller Hub (MCH)",
  "Chipset family supporting Gainestown and Harpertown processors",
  1,
  (select id from vendors where name="Intel")
);

-- CPUs like Xeon X5550 (Gainestown), X5470 (Harpertown), not Nehalem-EX or
-- Westmere-EX.
update uarches set chipset=(
  select id from chipsets where codename="Blackford"
) where name in ("Gainestown", "Harpertown");

insert into "chipsets" (
  codename, human_name, description, segment, vendor
) values (
  "Boxboro",
  "Intel® 7500 Chipset",
  "Chipset supporting Nehalem-EX, Westmere-EX, Itanium 9300",
  1,
  (select id from vendors where name="Intel")
);

-- E7540 (Beckton, Nehalem-EX), E7-4870 (Westmere-EX).
--
-- example motherboard, Supermicro X8QB6-F / X8QBE-F. described more in
-- https://www.supermicro.com/products/nfo/files/Xeon_7500/f_8-Core-MP.pdf
-- mentions 7500 Boxboro-EX chipset. see
-- https://www.intel.com/content/www/us/en/products/sku/49286/intel-7500-io-hub/specifications.html
-- and
-- https://www.intel.com/content/www/us/en/ark/products/codename/32633/products-formerly-boxboro.html
-- from docs, this chipset also supported Itanium 93xx?
update uarches set chipset=(
  select id from chipsets where codename="Boxboro"
) where name in ("Beckton", "Westmere");

-- CPUs like Xeon X3320 (Yorkfield), X3210 (Kentsfield), E3110 (Wolfdale), 3040
-- (Conroe)

-- Wolfdale, like E8400, paired with:
--  82x4x chipsets
--  82x3x chipsets
--  3210 Memory Controller

-- FILL IN

insert into "chipsets" (
  codename, human_name, description, segment, vendor
) values (
  "Mukilteo",
  "Intel® 3000 Memory Controller",
  "Memory controller for Kentsfield, Conroe, maybe Wolfdale and Yorkfield?",
  1,
  (select id from vendors where name="Intel")
);

-- Xeon 3040 (Conroe), Xeon X3210 (Kentsfield)
update uarches set chipset=(
  select id from chipsets where codename="Mukilteo"
) where name in ("Kentsfield", "Conroe");

-- X48 chipset?

-- Intel 3210 and Intel 3200 chipsets
-- https://www.intel.com/content/www/us/en/support/articles/000006688/server-products.html
-- lists support for Xeon 3300, 3200, 3100, 3000
-- https://www.intel.com/content/www/us/en/products/sku/34391/intel-3210-memory-controller/specifications.html
-- calls it Bigby
insert into "chipsets" (
  codename, human_name, description, segment, vendor
) values (
  "Bigby",
  "Intel® 3210 Memory Controller",
  "Memory controller for Conroe, Wolfdale, Kentsfield, and Yorkfield",
  1,
  (select id from vendors where name="Intel")
);

-- HELP: this clobbers the mention of Mukilteo. there's no provision of multiple
-- chipset product families supporting a particular CPU family. there should
-- be!
update uarches set chipset=(
  select id from chipsets where codename="Bigby"
) where name in ("Conroe", "Wolfdale", "Kentsfield", "Yorkfield");

-- this one's odd. it exists, has docs, but not clear where (if?) it's used
-- the product brief includes
-- '• Requires 50% less board space than prior-generation two-chip chipsets2'
-- ...
-- '2Comparison with Intel® E7520 Memory Controller Hub plus Intel® 6300ESB I/O
-- Controller Hub.'
-- as a point of comparison.
insert into "chipsets" (
  codename, human_name, description, segment, vendor
) values (
  NULL,
  "Intel® 3100 Chipset",
  NULL,
  1,
  (select id from vendors where name="Intel")
);

-- https://www.intel.com/content/www/us/en/products/sku/27743/intel-e7520-memory-controller/compatible.html
-- mentions Merom, Yonah, Dothan
insert into "chipsets" (
  codename, human_name, description, segment, vendor
) values (
  "Lindenhurst",
  "Intel® E7520 Memory Controller",
  "Memory controller for Merom and others",
  1,
  (select id from vendors where name="Intel")
);

update uarches set chipset=(
  select id from chipsets where codename="Lindenhurst"
) where name in ("Merom", "Yonah", "Dothan");

-- dunno which CPUs this was used with! but it existed.
insert into "chipsets" (
  codename, human_name, description, segment, vendor
) values (
  NULL,
  "Intel® E7320 Memory Controller",
  "Memory controller for unknown families",
  1,
  (select id from vendors where name="Intel")
);

-- dunno which CPUs this was used with! but it existed.
insert into "chipsets" (
  codename, human_name, description, segment, vendor
) values (
  "Plumas",
  "Intel® E7501 Memory Controller",
  "Memory controller for unknown families",
  1,
  (select id from vendors where name="Intel")
);

insert into "chipsets" (
  codename, human_name, description, segment, vendor
) values (
  "Calistoga",
  "Intel® 940 Series Chipsets",
  "Memory controller for unknown families, cohabitated with ICH7",
  1,
  (select id from vendors where name="Intel")
);

-- https://www.intel.com/content/www/us/en/products/sku/27730/intel-82p965-memory-controller/specifications.html
-- seems like mostly Conroe? also Cedar Mill Celerons.
insert into "chipsets" (
  codename, human_name, description, segment, vendor
) values (
  "Broadwater",
  "Intel® 960 Series Chipsets",
  "Memory controller for unknown families",
  1,
  (select id from vendors where name="Intel")
);

-- unclear what parts this supports..
insert into "chipsets" (
  codename, human_name, description, segment, vendor
) values (
  "Broadwater",
  "Intel® 975X Chipset",
  "Memory controller for unknown families",
  1,
  (select id from vendors where name="Intel")
);

-- Products formerly ICH9
-- https://www.intel.com/content/www/us/en/ark/products/codename/54291/products-formerly-ich9.html

-- Some Conroe parts like E6420 work with a few chipsets:
-- https://www.intel.com/content/www/us/en/products/sku/29755/intel-core2-duo-processor-e6420-4m-cache-2-13-ghz-1066-mhz-fsb/specifications.html
-- mentions
-- https://www.intel.com/content/www/us/en/products/sku/29755/intel-core2-duo-processor-e6420-4m-cache-2-13-ghz-1066-mhz-fsb/compatible.html
-- mentions 4-series 82G41, 82G45, 82P45, 82G43, 82X48

insert into "chipsets" (
  codename, human_name, description, segment, vendor
) values (
  "Eaglelake",
  "Intel® 4 Series Chipsets",
  "Most but not all 4x-series chipsets (G41, G45, P45, G43), not X48?",
  1,
  (select id from vendors where name="Intel")
);

insert into "chipsets" (
  codename, human_name, description, segment, vendor
) values (
  "Bearlake",
  "Intel® 3 Series Chipsets",
  "3x-series chipsets and X48 (??)",
  1,
  (select id from vendors where name="Intel")
);

-- old Intel processors could be found with Intel chipsets, or ServerWorks
-- chipsets.
-- the last ServerWorks chipset was around the P4 era.
-- ServerSet I
-- ServerSet II
-- ServerSet III
-- Champion
-- Grand Champion
