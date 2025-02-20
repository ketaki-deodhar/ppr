-- Post staging tables load step 1.
-- 1. Trim all character columns and set to null if empty.
-- 2. Set to null all dates that are the legacy default of 0001-01-01.
-- 3. Set default values for all flags that are empty characters
-- 4. Upddate duplicate document registration numbers to satisfy unique constraint.
UPDATE staging_mhr_manuhome
   SET MHSTATUS = (CASE WHEN MHSTATUS = '' THEN NULL ELSE MHSTATUS END),
       EXEMPTFL = (CASE WHEN EXEMPTFL = '' THEN NULL ELSE EXEMPTFL END),
       PRESOLD = (CASE WHEN PRESOLD = '' THEN NULL ELSE PRESOLD END),
       UPDATEID = (CASE WHEN TRIM(UPDATEID) = '' THEN NULL ELSE TRIM(UPDATEID) END),
       UPDATEDA = (CASE WHEN TRIM(UPDATEDA) = '' THEN NULL ELSE TRIM(UPDATEDA) END),
       UPDATETI = (CASE WHEN TRIM(UPDATETI) = '' THEN NULL ELSE TRIM(UPDATETI) END)
;


UPDATE staging_mhr_owngroup
   SET PENDING = (CASE WHEN TRIM(PENDING) = '' THEN NULL ELSE PENDING END),
       LESSEE = (CASE WHEN LESSEE = '' THEN NULL ELSE LESSEE END),
       LESSOR = (CASE WHEN LESSOR = '' THEN NULL ELSE LESSOR END),
       TENYSPEC = (CASE WHEN TRIM(TENYSPEC) = '' THEN 'Y' ELSE TENYSPEC END),
       CANDOCID = (CASE WHEN TRIM(CANDOCID) = '' THEN NULL ELSE TRIM(CANDOCID) END),
       INTEREST = (CASE WHEN TRIM(INTEREST) = '' THEN NULL ELSE TRIM(INTEREST) END)
;


UPDATE staging_mhr_note
   SET DESTROYD = (CASE WHEN TRIM(DESTROYD) = '' THEN 'N' ELSE DESTROYD END),
       DOCUTYPE = TRIM(DOCUTYPE),
       CANDOCID = (CASE WHEN TRIM(CANDOCID) = '' THEN NULL ELSE TRIM(CANDOCID) END),
       EXPIRYDA = (CASE WHEN TRIM(EXPIRYDA) = '' THEN NULL ELSE TRIM(EXPIRYDA) END),
       PHONE = (CASE WHEN TRIM(PHONE) = '' THEN NULL ELSE TRIM(PHONE) END),
       NAME = (CASE WHEN TRIM(NAME) = '' THEN NULL ELSE TRIM(NAME) END),
       ADDRESS = (CASE WHEN TRIM(ADDRESS) = '' THEN NULL ELSE TRIM(ADDRESS) END),
       REMARKS = (CASE WHEN TRIM(REMARKS) = '' THEN NULL ELSE TRIM(REMARKS) END)
;


UPDATE staging_mhr_owner
   SET VERIFIED = (CASE WHEN VERIFIED = '' THEN NULL ELSE VERIFIED END),
       COMPNAME = TRIM(COMPNAME),
       OWNRFONE = (CASE WHEN TRIM(OWNRFONE) = '' THEN NULL ELSE TRIM(OWNRFONE) END),
       OWNRPOCO = (CASE WHEN TRIM(OWNRPOCO) = '' THEN NULL ELSE TRIM(OWNRPOCO) END),
       OWNRNAME = (CASE WHEN TRIM(OWNRNAME) = '' THEN NULL ELSE TRIM(OWNRNAME) END),
       OWNRADDR = (CASE WHEN TRIM(OWNRADDR) = '' THEN NULL ELSE TRIM(OWNRADDR) END),
       OWNRSUFF = (CASE WHEN TRIM(OWNRSUFF) = '' THEN NULL ELSE TRIM(OWNRSUFF) END)
;


UPDATE staging_mhr_location
   SET TAXCERT = (CASE WHEN TRIM(TAXCERT) = '' THEN 'N' ELSE TAXCERT END),
       CANDOCID = (CASE WHEN TRIM(CANDOCID) = '' THEN NULL ELSE TRIM(CANDOCID) END),
       STNUMBER = (CASE WHEN TRIM(STNUMBER) = '' THEN NULL ELSE TRIM(STNUMBER) END),
       STNAME = (CASE WHEN TRIM(STNAME) = '' THEN NULL ELSE TRIM(STNAME) END),
       TOWNCITY = (CASE WHEN TRIM(TOWNCITY) = '' THEN NULL ELSE TRIM(TOWNCITY) END),
       PROVINCE = (CASE WHEN TRIM(PROVINCE) = '' THEN NULL ELSE TRIM(PROVINCE) END),
       BCAAAREA = (CASE WHEN TRIM(BCAAAREA) = '' THEN NULL ELSE TRIM(BCAAAREA) END),
       BCAAJURI = (CASE WHEN TRIM(BCAAJURI) = '' THEN NULL ELSE TRIM(BCAAJURI) END),
       BCAAROLL = (CASE WHEN TRIM(BCAAROLL) = '' THEN NULL ELSE TRIM(BCAAROLL) END),
       MAHPNAME = (CASE WHEN TRIM(MAHPNAME) = '' THEN NULL ELSE TRIM(MAHPNAME) END),
       MAHPPAD = (CASE WHEN TRIM(MAHPPAD) = '' THEN NULL ELSE TRIM(MAHPPAD) END),
       PIDNUMB = (CASE WHEN TRIM(PIDNUMB) = '' THEN NULL ELSE TRIM(PIDNUMB) END),
       LOT = (CASE WHEN TRIM(LOT) = '' THEN NULL ELSE TRIM(LOT) END),
       PARCEL = (CASE WHEN TRIM(PARCEL) = '' THEN NULL ELSE TRIM(PARCEL) END),
       BLOCK = (CASE WHEN TRIM(BLOCK) = '' THEN NULL ELSE TRIM(BLOCK) END),
       DISTLOT = (CASE WHEN TRIM(DISTLOT) = '' THEN NULL ELSE TRIM(DISTLOT) END),
       PARTOF = (CASE WHEN TRIM(PARTOF) = '' THEN NULL ELSE TRIM(PARTOF) END),
       SECTION = (CASE WHEN TRIM(SECTION) = '' THEN NULL ELSE TRIM(SECTION) END),
       TOWNSHIP = (CASE WHEN TRIM(TOWNSHIP) = '' THEN NULL ELSE TRIM(TOWNSHIP) END),
       MERIDIAN = (CASE WHEN TRIM(MERIDIAN) = '' THEN NULL ELSE TRIM(MERIDIAN) END),
       LANDDIST = (CASE WHEN TRIM(LANDDIST) = '' THEN NULL ELSE TRIM(LANDDIST) END),
       TAXDATE = (CASE WHEN TRIM(TAXDATE) = '' THEN NULL ELSE TRIM(TAXDATE) END),
       LEAVEBC = (CASE WHEN TRIM(LEAVEBC) = '' THEN 'N' ELSE LEAVEBC END),
       EXCPLAN = (CASE WHEN TRIM(EXCPLAN) = '' THEN NULL ELSE TRIM(EXCPLAN) END),
       MHDEALER = (CASE WHEN TRIM(MHDEALER) = '' THEN NULL ELSE TRIM(MHDEALER) END),
       ADDDESC = (CASE WHEN TRIM(ADDDESC) = '' THEN NULL ELSE TRIM(ADDDESC) END),
       PLAN = (CASE WHEN TRIM(PLAN) = '' THEN NULL ELSE TRIM(PLAN) END),
       RANGE = (CASE WHEN TRIM(RANGE) = '' THEN NULL ELSE TRIM(RANGE) END)
;


UPDATE staging_mhr_description
   SET CIRCA = (CASE WHEN TRIM(CIRCA) = '' THEN 'N' ELSE CIRCA END),
       CANDOCID = (CASE WHEN TRIM(CANDOCID) = '' THEN NULL ELSE TRIM(CANDOCID) END),
       CSANUMBR = (CASE WHEN TRIM(CSANUMBR) = '' THEN NULL ELSE TRIM(CSANUMBR) END),
       CSASTAND = (CASE WHEN TRIM(CSASTAND) = '' THEN NULL ELSE TRIM(CSASTAND) END),
       YEARMADE = (CASE WHEN TRIM(YEARMADE) = '' THEN NULL ELSE TRIM(YEARMADE) END),
       SERNUMB1 = (CASE WHEN TRIM(SERNUMB1) = '' THEN NULL ELSE TRIM(SERNUMB1) END),
       SERNUMB2 = (CASE WHEN TRIM(SERNUMB2) = '' THEN NULL ELSE TRIM(SERNUMB2) END),
       SERNUMB3 = (CASE WHEN TRIM(SERNUMB3) = '' THEN NULL ELSE TRIM(SERNUMB3) END),
       SERNUMB4 = (CASE WHEN TRIM(SERNUMB4) = '' THEN NULL ELSE TRIM(SERNUMB4) END),
       ENGIDATE = (CASE WHEN TRIM(ENGIDATE) = '' THEN NULL ELSE TRIM(ENGIDATE) END),
       ENGINAME = (CASE WHEN TRIM(ENGINAME) = '' THEN NULL ELSE TRIM(ENGINAME) END),
       MANUNAME = (CASE WHEN TRIM(MANUNAME) = '' THEN NULL ELSE TRIM(MANUNAME) END),
       MAKEMODL = (CASE WHEN TRIM(MAKEMODL) = '' THEN NULL ELSE TRIM(MAKEMODL) END),
       REBUILTR = (CASE WHEN TRIM(REBUILTR) = '' THEN NULL ELSE TRIM(REBUILTR) END),
       OTHERREM = (CASE WHEN TRIM(OTHERREM) = '' THEN NULL ELSE TRIM(OTHERREM) END)
;

UPDATE staging_mhr_description
   SET circa = 'Y'
 WHERE circa = '?'
;
UPDATE staging_mhr_description
   SET yearmade = '0'
 WHERE yearmade LIKE '%?%'
;
UPDATE staging_mhr_description
   SET yearmade = '1970'
 WHERE yearmade = '197O'
;
UPDATE staging_mhr_description
   SET yearmade = '1981'
 WHERE yearmade = '198L'
;


UPDATE staging_mhr_document
   SET INTERIMD = (CASE WHEN TRIM(INTERIMD) = '' THEN NULL ELSE INTERIMD END),
       OWNLAND = (CASE WHEN TRIM(OWNLAND) = '' THEN 'N' ELSE OWNLAND END),
       LASTSERV = (CASE WHEN TRIM(LASTSERV) = '' THEN NULL ELSE LASTSERV END),
       DOCUTYPE = TRIM(DOCUTYPE),
       DRAFDATE = (CASE WHEN TRIM(DRAFDATE) = '' THEN NULL ELSE TRIM(DRAFDATE) END),
       REGIDATE = (CASE WHEN TRIM(REGIDATE) = '' THEN NULL ELSE TRIM(REGIDATE) END),
       OWNRXREF = (CASE WHEN TRIM(OWNRXREF) = '' THEN NULL ELSE TRIM(OWNRXREF) END),
       RSLIPNUM = (CASE WHEN TRIM(RSLIPNUM) = '' THEN NULL ELSE TRIM(RSLIPNUM) END),
       BCOLACCT = (CASE WHEN TRIM(BCOLACCT) = '' THEN NULL ELSE TRIM(BCOLACCT) END),
       DATNUMBR = (CASE WHEN TRIM(DATNUMBR) = '' THEN NULL ELSE TRIM(DATNUMBR) END),
       EXAMINID = (CASE WHEN TRIM(EXAMINID) = '' THEN NULL ELSE TRIM(EXAMINID) END),
       UPDATEID = (CASE WHEN TRIM(UPDATEID) = '' THEN NULL ELSE TRIM(UPDATEID) END),
       PHONE = (CASE WHEN TRIM(PHONE) = '' THEN NULL ELSE TRIM(PHONE) END),
       ATTNREF = (CASE WHEN TRIM(ATTNREF) = '' THEN NULL ELSE TRIM(ATTNREF) END),
       NAME = (CASE WHEN TRIM(NAME) = '' THEN NULL ELSE TRIM(NAME) END),
       ADDRESS = (CASE WHEN TRIM(ADDRESS) = '' THEN NULL ELSE TRIM(ADDRESS) END),
       DATEOFEX = (CASE WHEN TRIM(DATEOFEX) = '' THEN NULL ELSE TRIM(DATEOFEX) END),
       CONVALUE = (CASE WHEN TRIM(CONVALUE) = '' THEN NULL ELSE TRIM(CONVALUE) END),
       AFFIRMBY = (CASE WHEN TRIM(AFFIRMBY) = '' THEN NULL ELSE TRIM(AFFIRMBY) END),
       CONSENT = (CASE WHEN TRIM(CONSENT) = '' THEN NULL ELSE TRIM(CONSENT) END),
       OLBCFOLI = (CASE WHEN TRIM(OLBCFOLI) = '' THEN NULL ELSE TRIM(OLBCFOLI) END)
;


-- ~329000 records
UPDATE staging_mhr_document
   SET dateofex = NULL
 WHERE dateofex = '0001-01-01'
;

UPDATE staging_mhr_note
   SET EXPIRYDA = NULL
 WHERE EXPIRYDA = '0001-01-01'
;

-- ~115000 records
UPDATE staging_mhr_description
   SET ENGIDATE = NULL
 WHERE ENGIDATE = '0001-01-01'
;

-- ~180000 records
UPDATE staging_mhr_location
   SET TAXDATE = NULL
 WHERE TAXDATE = '0001-01-01'
;

-- Remove duplicate violation of integrity constraint
UPDATE staging_mhr_document
   SET docuregi = '00D91791'
 WHERE documtid = '43446039'
   AND docuregi = '00091791'
;
UPDATE staging_mhr_document
   SET docuregi = '00D91859'
 WHERE documtid = '42442794'
   AND docuregi = '00091859'
;
UPDATE staging_mhr_document
   SET docuregi = '00D95630'
 WHERE documtid = '43327140'
   AND docuregi = '00095630'
;
UPDATE staging_mhr_document
   SET docuregi = '0D171286'
 WHERE documtid = '41331567'
   AND docuregi = '00171286'
;
