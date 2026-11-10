"""One entry per metro. Field maps go from our schema to the layer's field names.
`addr` may be a list of fields joined with spaces. `where` should keep the pull small: residential
land use and a server-side absentee filter (mail zip differs or out of state); parcels that carry a
signal are fetched by id afterwards, so nothing with a signal is lost."""

MARICOPA_P = "https://services.arcgis.com/ykpntM6e3tHvzKRJ/arcgis/rest/services/Parcels_view/FeatureServer/0"
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
}
