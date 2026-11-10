# Charlotte (Mecklenburg County) sources

Working, free, unattended:
- Mecklenburg `meckgis.mecklenburgcountync.gov/server/rest/services/TaxParcel_Camaownershipvalues/FeatureServer/0` (430k; owner, mailing address, situs address with city, total value, property use, last sale). Single family is `txt_propertyuse_desc LIKE 'SINGLE%'` (292k). Absentee pulled server side as out of state or mail city different from the situs jurisdiction. No year built or living area on this layer, so the "real house" test uses the street number only; `TaxParcel_camadata` has land use codes if needed later.
- City of Charlotte HNS `CodeEnforcementNewAndOpenCases/MapServer/0` (3.1k open: Housing 1k, Nuisance, Zoning, Parking, Graffiti) and `CodeEnforcementOrderstoDemolish/MapServer/0` (14). `ParcelId` is space padded.
- County `VacantParcels` (26k, mostly land) not used.

Next: Mecklenburg tax foreclosure list (county attorney posts it), Clerk of Court foreclosure notices (judicial state), code cases in the towns outside Charlotte.
