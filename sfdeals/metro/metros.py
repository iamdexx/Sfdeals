"""One entry per metro. Field maps go from our schema to the layer's field names.
`addr` may be a list of fields joined with spaces. `where` should keep the pull small: residential
land use and a server-side absentee filter (mail zip differs or out of state); parcels that carry a
signal are fetched by id afterwards, so nothing with a signal is lost."""

MARICOPA_P = "https://services.arcgis.com/ykpntM6e3tHvzKRJ/arcgis/rest/services/Parcels_view/FeatureServer/0"
HCPA_P = "https://services.arcgis.com/apTfC6SUmnNfnxuF/arcgis/rest/services/HCPA_Parcels_Daily/FeatureServer/0"
MECK_P = "https://meckgis.mecklenburgcountync.gov/server/rest/services/TaxParcel_Camaownershipvalues/FeatureServer/0"
CLT_CODE = "https://gis.charlottenc.gov/arcgis/rest/services/HNS/"
MARICOPA_L = "https://services.arcgis.com/ykpntM6e3tHvzKRJ/arcgis/rest/services/ParcelLienDelinquent/FeatureServer/"

METROS = {
    "phx": {
        "name": "Phoenix, AZ", "short": "Phoenix", "state": "AZ", "min_value": 60000,
        "counties": [{
            "name": "Maricopa County",
            "parcels": {
                "url": MARICOPA_P, "page": 2000,
                "where": "PUC LIKE '01%' AND (MAIL_ZIP <> PHYSICAL_ZIP OR MAIL_STATE <> 'AZ')",
                "map": {"tag": "APN", "addr": ["PHYSICAL_STREET_NUM", "PHYSICAL_STREET_DIR", "PHYSICAL_STREET_NAME", "PHYSICAL_STREET_TYPE", "PHYSICAL_STREET_POSTDIR"],
                        "zip": "PHYSICAL_ZIP", "muni": "PHYSICAL_CITY", "owner": "OWNER_NAME", "mail": "MAIL_ADDR1", "mail_city": "MAIL_CITY",
                        "mail_state": "MAIL_STATE", "mail_zip": "MAIL_ZIP", "landuse": "PUC", "year": "CONST_YEAR", "res_sqft": "LIVING_SPACE",
                        "value": "FCV_CUR", "sale_date": "SALE_DATE", "sale_price": "SALE_PRICE"},
            },
            "signals": [
                {"name": "taxsale", "weight": 45, "label": "tax lien unsold, state held",
                 "url": MARICOPA_L + "1", "map": {"tag": "APN", "addr": "PropertyFullStreetAddress", "link": "TreasurerWebLink"}},
                {"name": "taxlien", "weight": 35, "label": "delinquent tax, lien list",
                 "url": MARICOPA_L + "2", "map": {"tag": "APN", "addr": "PropertyFullStreetAddress", "link": "TreasurerWebLink"}},
            ],
            "lookup": "https://mcassessor.maricopa.gov/mcs/?q={tag}",
        }],
    },
    "tpa": {
        "name": "Tampa, FL", "short": "Tampa", "state": "FL", "min_value": 60000,
        "counties": [{
            "name": "Hillsborough County",
            "parcels": {
                "url": HCPA_P, "page": 2000,
                # FL DOR use 01 = single family. No homestead exemption = not the owner's home.
                "where": "DOR_C LIKE '01%' AND OWNER NOT LIKE '%CONFIDENTIAL%' AND (HX_YEAR IS NULL OR HX_YEAR = 0 OR STATE <> 'FL' OR B1_COND_DSC = 'Poor')",
                "map": {"tag": "FOLIO", "addr": "SITE_ADDR", "zip": "SITE_ZIP", "muni": "SITE_CITY", "owner": "OWNER", "mail": "ADDR_1",
                        "mail_city": "CITY", "mail_state": "STATE", "mail_zip": "ZIP", "landuse": "DOR_C", "units": "tUNITS", "year": "ACT",
                        "res_sqft": "HEAT_AR", "value": "JUST", "sale_price": "SALE1_PRC"},
                "occ_field": "HX_YEAR",
                "extra": ["B1_COND_DSC", "SALE1_DEED_DSC", "SALE1_DATE", "PERMIT_COUNT"],
            },
            "signals": [],
            "derived": [
                {"name": "condition", "weight": 35, "label": "building condition poor (appraiser)", "field": "B1_COND_DSC", "in": ["Poor"]},
                {"name": "estate", "weight": 25, "label": "estate or guardian deed in the last 2 years", "field": "SALE1_DEED_DSC",
                 "in": ["Personal Representative", "Guardians"], "since_field": "SALE1_DATE", "since_days": 730},
                {"name": "quitclaim", "weight": 15, "label": "quit claim transfer in the last 2 years", "field": "SALE1_DEED_DSC",
                 "in": ["Quit Claim"], "since_field": "SALE1_DATE", "since_days": 730},
                {"name": "taxdeed", "weight": 20, "label": "sold at tax deed or sheriff sale in the last 2 years", "field": "SALE1_DEED_DSC",
                 "in": ["Tax", "Sheriffs", "Masters"], "since_field": "SALE1_DATE", "since_days": 730},
            ],
            "lookup": "https://gis.hcpafl.org/propertysearch/#/parcel/basic/{tag}",
        }],
    },
    "clt": {
        "name": "Charlotte, NC", "short": "Charlotte", "state": "NC", "min_value": 60000,
        "counties": [{
            "name": "Mecklenburg County",
            "parcels": {
                "url": MECK_P, "page": 2000,
                "where": "txt_propertyuse_desc LIKE 'SINGLE%' AND (txt_state <> 'NC' OR txt_city <> situsaddress1juris)",
                "map": {"tag": "pid", "addr": "situsaddress1", "muni": "situsaddress1juris", "owner": "full_owner_name", "mail": "txt_mailaddr1",
                        "mail_city": "txt_city", "mail_state": "txt_state", "mail_zip": "txt_zipcode", "landuse": "txt_propertyuse_desc",
                        "value": "amt_totalvalue", "sale_price": "amt_price"},
                "addr_strip": r"\s+(CHARLOTTE|MATTHEWS|MINT HILL|HUNTERSVILLE|CORNELIUS|DAVIDSON|PINEVILLE|STALLINGS)?\s*NC$",
            },
            "signals": [
                {"name": "demolish", "weight": 45, "label": "order to demolish (city code enforcement)", "url": CLT_CODE + "CodeEnforcementOrderstoDemolish/MapServer/0",
                 "map": {"tag": "ParcelId", "addr": "FullAddress", "case": "CaseNumber", "kind": "CaseType", "status": "CaseStatus"}},
                {"name": "housing_case", "weight": 25, "label": "open housing code case (city)", "url": CLT_CODE + "CodeEnforcementNewAndOpenCases/MapServer/0",
                 "where": "CaseType = 'Housing'", "map": {"tag": "ParcelId", "addr": "FullAddress", "case": "CaseNumber", "kind": "CaseType", "status": "CaseStatus"}},
                {"name": "nuisance_case", "weight": 15, "label": "open nuisance case (city)", "url": CLT_CODE + "CodeEnforcementNewAndOpenCases/MapServer/0",
                 "where": "CaseType = 'Nuisance'", "map": {"tag": "ParcelId", "addr": "FullAddress", "case": "CaseNumber", "kind": "CaseType", "status": "CaseStatus"}},
            ],
            "lookup": "https://property.spatialest.com/nc/mecklenburg/#/property/{tag}",
        }],
    },
}
