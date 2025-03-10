alter table families add column doc_item;

-- HELP! "segments" probably should not be defined *here*, it's a more general
-- concept than just to do with chipsets.
--
-- "segments" refers to product segments. primarily this is just "ulp/mobile",
-- "low power/laptop", "consumer/desktop/client",
-- "enthusiast/high-end desktop (HEDT)", "workstation/server". sometimes the
-- intersection for a part is HEDT/workstation, lines can be blurry.
--
-- this is mostly useful because chipsets themselves are sometimes paired off
-- with hardware in a segment-specific way, particularly hardware in the 2010s
-- as "chipsets" have started integrating more and more of the rest of a
-- mainboard's functionality.
create table "segments" (
  id INTEGER PRIMARY KEY,
  name TEXT
);

-- just an intermediate table to support linking different kinds of records
-- (chipsets, uarches, etc) to docs.
create table "doc_items" (
  id INTEGER PRIMARY KEY
);

-- glue table between doc_items and docs. one document may be in multiple
-- document sets (Intel 7 Series Platform Controller Hub describes all the _7_
-- chipsets and C216, for example). one document set likely has multiple
-- documents.
create table "doc_links" (
  id INTEGER PRIMARY KEY,
  doc_item INTEGER,
  doc INTEGER
);

-- closest thing to an enum we're getting here. just need to be able to
-- categorize docs as being vendor reference material, vendor marketing
-- material, external reference, etc
create table "doc_kind" (
  id INTEGER PRIMARY KEY,
  name TEXT
);

insert into "doc_kind" (name) values ("vendor reference");
insert into "doc_kind" (name) values ("vendor marketing");
insert into "doc_kind" (name) values ("external reference");

create table "docs" (
  id INTEGER PRIMARY KEY,
  title TEXT,
  description TEXT,
  published TEXT, -- timestamp kinda thing. may be just a year, maybe MMYYYY.
  source TEXT,
  kind INTEGER NOT NULL
);

insert into "docs" (title, description, published, source, kind) values (
  "Intel® 7 Series / C216 Chipset Family Platform Controller Hub (PCH)",
  "Order Number: 326776-003",
  "June 2012",
  "https://www.intel.com/content/dam/www/public/us/en/documents/datasheets/7-series-chipset-pch-datasheet.pdf",
  (select id from "doc_kind" where name="vendor reference")
);

insert into "docs" (title, description, published, source, kind) values (
  "Intel® 6 Series Chipset and Intel® C200 Series Chipset",
  "Document Number: 324645-006",
  "May 2011",
  "https://www.intel.com/content/dam/www/public/us/en/documents/datasheets/6-chipset-c200-chipset-datasheet.pdf",
  (select id from "doc_kind" where name="vendor reference")
);

insert into "docs" (title, description, published, source, kind) values (
  "Intel® 6 Series Chipset and Intel® C200 Series Chipset Specification Update",
  "Document Number: 324646-005",
  "April 2011",
  "https://www.intel.com/content/dam/support/us/en/documents/boardsandkits/Intel-6-Series-Chipset-Specification-Update.pdf",
  (select id from "doc_kind" where name="vendor reference")
);

insert into "docs" (title, description, published, source, kind) values (
  "Intel® 5 Series Chipset and Intel® 3400 Series Chipset",
  "Order Number: 322169-004",
  "January 2012",
  "https://www.intel.com/content/dam/www/public/us/en/documents/datasheets/5-chipset-3400-chipset-datasheet.pdf",
  (select id from "doc_kind" where name="vendor reference")
);

insert into "docs" (title, description, published, source, kind) values (
  "Product Brief, Intel® X48 Express Chipset",
  NULL,
  "2008",
  "https://www.intel.com/Assets/PDF/prodbrief/319646.pdf",
  (select id from "doc_kind" where name="vendor reference")
);

insert into "docs" (title, description, published, source, kind) values (
  "Intel® 4 Series Chipset Family",
  "Document Number: 319970-007",
  "March 2010",
  "https://www.intel.com/content/dam/www/public/us/en/documents/datasheets/4-chipset-family-datasheet.pdf",
  (select id from "doc_kind" where name="vendor reference")
);

insert into "docs" (title, description, published, source, kind) values (
  "Intel® 3 Series Chipset Family",
  "Document Number: 316966-002",
  "August 2007",
  "https://www.intel.com/Assets/PDF/datasheet/316966.pdf",
  (select id from "doc_kind" where name="vendor reference")
);

insert into "docs" (title, description, published, source, kind) values (
  "Intel® 7500 Chipset",
  "Reference Number: 322827-001",
  "March 2010",
  "https://www.intel.com/content/dam/doc/datasheet/7500-chipset-datasheet.pdf",
  (select id from "doc_kind" where name="vendor reference")
);

insert into "docs" (title, description, published, source, kind) values (
  "Intel® I/O Controller Hub 10 (ICH10) Family",
  "Document Number: 319973-003",
  "October 2008",
  "https://www.intel.sg/content/dam/doc/datasheet/io-controller-hub-10-family-datasheet.pdf",
  (select id from "doc_kind" where name="vendor reference")
);

insert into "docs" (title, description, published, source, kind) values (
  "Intel® S5000 Server Board Family Datasheet",
  "Intel order number D38960-006",
  "Auguest 31, 2007",
  "https://cdrdv2.intel.com/v1/dl/getContent/841078?fileName=d38960006_s5000datasheet.pdf",
  (select id from "doc_kind" where name="vendor reference")
);

insert into "docs" (title, description, published, source, kind) values (
  "Intel® 5000P/5000V/5000Z Chipset Memory Controller Hub (MCH)",
  "Document Number: 313071-003",
  "September 2006",
  "https://www.intel.com/content/dam/doc/datasheet/5000p-5000v-5000z-chipset-memory-controller-hub-datasheet.pdf",
  (select id from "doc_kind" where name="vendor reference")
);

insert into "docs" (title, description, published, source, kind) values (
  "Intel® 3000 and 3010 Chipset Memory Controller Hub (MCH)",
  "Reference Number: 313953 Revision: 002",
  "November 2008",
  "https://theretroweb.com/chip/documentation/3010datasheet-64b138b225e4f836032787.pdf",
  (select id from "doc_kind" where name="vendor reference")
);

insert into "docs" (title, description, published, source, kind) values (
  "Intel® 3100 Chipset",
  "Order Number: 313458-007US",
  "October 2008",
  "https://theretroweb.com/chipset/documentation/31345803-66964e3e39020092274066.pdf",
  (select id from "doc_kind" where name="vendor reference")
);

insert into "docs" (title, description, published, source, kind) values (
  "Product Brief, Intel® 3100 Chipset",
  NULL,
  "2007",
  "https://theretroweb.com/chipset/documentation/27-45931-66964e3e3846e800927612.pdf",
  (select id from "doc_kind" where name="vendor marketing")
);

insert into "docs" (title, description, published, source, kind) values (
  "Intel® 3200 and 3210 Chipset Memory Controller Hub (MCH)",
  "Document Number: 318463-001",
  "November 2007",
  "https://xonstorage.blob.core.windows.net/pdf/intel_nu3210mcsljef_apr22_xonlink.pdf",
  (select id from "doc_kind" where name="vendor reference")
);

-- are there other docs for other ICH7 embeddings?
insert into "docs" (title, description, published, source, kind) values (
  "Intel® I/O Controller Hub 7 (ICH7) Family",
  "Document Number: 307013-003 - For the Intel® 82801GB ICH7, 82801GR ICH7R, 82801GDH ICH7DH, 82801GBM ICH7-M, 82801GHM ICH7-M DH, and 82801GU ICH7-U I/O Controller Hubs",
  "April 2007",
  "https://theretroweb.com/chip/documentation/i-o-controller-hub-7-datasheet-6623110df0c5c325585792.pdf",
  (select id from "doc_kind" where name="vendor reference")
);

insert into "docs" (title, description, published, source, kind) values (
  "Intel® E7520 Memory Controller Hub (MCH)",
  "Document Number: 303006-002",
  "February 2005",
  "https://www.intel.com/content/dam/doc/datasheet/e7520-memory-controller-hub-datasheet.pdf",
  (select id from "doc_kind" where name="vendor reference")
);

insert into "docs" (title, description, published, source, kind) values (
  "Intel® E7501 Memory Controller Hub (MCH)",
  "Document Number: 251927-002",
  "July 2003",
  "http://datasheet.elcodis.com/pdf2/76/38/763894/qg82945gm.pdf",
  (select id from "doc_kind" where name="vendor reference")
);

insert into "docs" (title, description, published, source, kind) values (
  "Intel® E7501 Memory Controller Hub (MCH) Specification Update",
  "Document Number: 251927-002",
  "July 2003",
  "https://peertje.daanberg.net/drivers/intel/download.intel.com/design/chipsets/specupdt/25192803.pdf",
  (select id from "doc_kind" where name="vendor reference")
);

insert into "docs" (title, description, published, source, kind) values (
  "Intel® E7320 Memory Controller Hub (MCH)",
  "Document Number: 303007-002",
  "February 2005",
  "https://www.intel.com/content/dam/doc/datasheet/e7320-memory-controller-hub-datasheet.pdf",
  (select id from "doc_kind" where name="vendor reference")
);

insert into "docs" (title, description, published, source, kind) values (
  "Intel® E7500/E7501/E7505 Chipset Thermal Design Guide",
  "Document Number: 298647-003",
  "December 2002",
  "https://www.intel.co.jp/content/dam/doc/design-guide/e7500-e7501-e7505-chipset-guide.pdf",
  (select id from "doc_kind" where name="vendor reference")
);

insert into "docs" (title, description, published, source, kind) values (
  "Mobile Intel® 945 Express Chipset Family",
  "Document Number: 309219-006",
  "June 2008",
  "https://www.intel.com/content/dam/www/public/us/en/documents/datasheets/mobile-945-express-chipset-datasheet.pdf",
  (select id from "doc_kind" where name="vendor reference")
);

insert into "docs" (title, description, published, source, kind) values (
  "Intel® 965 Express Chipset Family",
  "Document Number: 313053-002",
  "July 2006",
  "https://www.intel.com/Assets/PDF/datasheet/313053.pdf",
  (select id from "doc_kind" where name="vendor reference")
);

insert into "docs" (title, description, published, source, kind) values (
  "Intel® 975X Chipset for 82975X Memory Controller Hub",
  "Document Number: 310158-001",
  "November 2005",
  "https://www.intel.com/Assets/PDF/datasheet/310158.pdf",
  (select id from "doc_kind" where name="vendor reference")
);

insert into "docs" (title, description, published, source, kind) values (
  "Intel®Atom™ Processor C3000 Product Family Integrated 10 GbE LAN Controller Programmer's Reference Manual (PRM)",
  "Document # 338653-003",
  "November 2020",
  "https://cdrdv2-public.intel.com/338653/338653%20Denverton_PRM_v_1_8.pdf",
  (select id from "doc_kind" where name="vendor reference")
);

insert into "doc_items" (id) values (NULL);

insert into "doc_links" (doc_item, doc) values (
  (select count(*) from doc_items),
  (select id from docs where title="Intel® 7 Series / C216 Chipset Family Platform Controller Hub (PCH)")
);

update chipsets
  set doc_item=(select count(*) from doc_items)
  where codename="Panther Point";

insert into "doc_items" (id) values (NULL);

insert into "doc_links" (doc_item, doc) values (
  (select count(*) from doc_items),
  (select id from docs where title="Intel® 6 Series Chipset and Intel® C200 Series Chipset")
);

insert into "doc_links" (doc_item, doc) values (
  (select count(*) from doc_items),
  (select id from docs where title="Intel® 6 Series Chipset and Intel® C200 Series Chipset Specification Update")
);

update chipsets
  set doc_item=(select count(*) from doc_items)
  where codename="Cougar Point";

insert into "doc_items" (id) values (NULL);

insert into "doc_links" (doc_item, doc) values (
  (select count(*) from doc_items),
  (select id from docs where title="Intel® 5 Series Chipset and Intel® 3400 Series Chipset")
);

update chipsets
  set doc_item=(select count(*) from doc_items)
  where codename="Ibex Point";

insert into "doc_items" (id) values (NULL);

insert into "doc_links" (doc_item, doc) values (
  (select count(*) from doc_items),
  (select id from docs where title="Intel® 4 Series Chipset Family")
);

update chipsets
  set doc_item=(select count(*) from doc_items)
  where codename="Eaglelake";

insert into "doc_items" (id) values (NULL);

insert into "doc_links" (doc_item, doc) values (
  (select count(*) from doc_items),
  (select id from docs where title="Product Brief, Intel® X48 Express Chipset")
);

insert into "doc_links" (doc_item, doc) values (
  (select count(*) from doc_items),
  (select id from docs where title="Intel® 3 Series Chipset Family")
);

update chipsets
  set doc_item=(select count(*) from doc_items)
  where codename="Bearlake";

insert into "doc_items" (id) values (NULL);

insert into "doc_links" (doc_item, doc) values (
  (select count(*) from doc_items),
  (select id from docs where title="Intel® 7500 Chipset")
);

update chipsets
  set doc_item=(select count(*) from doc_items)
  where codename="Boxboro";

insert into "doc_items" (id) values (NULL);

insert into "doc_links" (doc_item, doc) values (
  (select count(*) from doc_items),
  (select id from docs where title="Intel® 5000P/5000V/5000Z Chipset Memory Controller Hub (MCH)")
);

update chipsets
  set doc_item=(select count(*) from doc_items)
  where codename="Blackford";

insert into "doc_items" (id) values (NULL);

insert into "doc_links" (doc_item, doc) values (
  (select count(*) from doc_items),
  (select id from docs where title="Intel® 3000 and 3010 Chipset Memory Controller Hub (MCH)")
);

insert into "doc_links" (doc_item, doc) values (
  (select count(*) from doc_items),
  (select id from docs where title="Intel® I/O Controller Hub 7 (ICH7) Family")
);

update chipsets
  set doc_item=(select count(*) from doc_items)
  where codename="Mukilteo";

insert into "doc_items" (id) values (NULL);

insert into "doc_links" (doc_item, doc) values (
  (select count(*) from doc_items),
  (select id from docs where title="Intel® 3200 and 3210 Chipset Memory Controller Hub (MCH)")
);

update chipsets
  set doc_item=(select count(*) from doc_items)
  where codename="Bigby";

-- see chipsets.sql, the 3100 chipset is ... weird?
insert into "doc_items" (id) values (NULL);

insert into "doc_links" (doc_item, doc) values (
  (select count(*) from doc_items),
  (select id from docs where title="Intel® 3100 Chipset")
);

insert into "doc_links" (doc_item, doc) values (
  (select count(*) from doc_items),
  (select id from docs where title="Product Brief, Intel® 3100 Chipset")
);

update chipsets
  set doc_item=(select count(*) from doc_items)
  where human_name="Intel® 3100 Chipset";

insert into "doc_items" (id) values (NULL);

insert into "doc_links" (doc_item, doc) values (
  (select count(*) from doc_items),
  (select id from docs where title="Intel® E7520 Memory Controller Hub (MCH)")
);

update chipsets
  set doc_item=(select count(*) from doc_items)
  where human_name="Intel® E7520 Memory Controller";

insert into "doc_items" (id) values (NULL);

insert into "doc_links" (doc_item, doc) values (
  (select count(*) from doc_items),
  (select id from docs where title="Mobile Intel® 945 Express Chipset Family")
);

insert into "doc_links" (doc_item, doc) values (
  (select count(*) from doc_items),
  (select id from docs where title="Intel® I/O Controller Hub 7 (ICH7) Family")
);

update chipsets
  set doc_item=(select count(*) from doc_items)
  where human_name="Intel® 940 Series Chipsets";

insert into "doc_items" (id) values (NULL);

insert into "doc_links" (doc_item, doc) values (
  (select count(*) from doc_items),
  (select id from docs where title="Mobile Intel® 965 Express Chipset Family")
);

update chipsets
  set doc_item=(select count(*) from doc_items)
  where human_name="Intel® 960 Series Chipsets";

insert into "doc_items" (id) values (NULL);

insert into "doc_links" (doc_item, doc) values (
  (select count(*) from doc_items),
  (select id from docs where title="Intel® 975X Chipset for 82975X Memory Controller Hub")
);

update chipsets
  set doc_item=(select count(*) from doc_items)
  where human_name="Intel® 975X Chipset";

