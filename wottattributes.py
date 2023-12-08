"""
Valid attributes for Rider, Environment, Simulation, and IPCalculator.
Model and View are dependent on this, instead of being dependent on each other
"""

class RiderAttributes(object):
    RIDERID = "riderID"
    FIRSTNAME = "firstName"
    LASTNAME = "lastName"
    WEIGHT = "massKG"
    FTP = "FTP"
    WPRIME = "wPrime"
    CDA = "CdA"
    POWERRESULTS = "powerResults"

class EnvirAttributes(object):
    ENVIRID = "envirID"
    ENVIRNAME = "envirName"
    AIRDENSITY = "airDensity"
    CRR = "Crr"
    MECHLOSSES = "mechLosses"

class SimAttributes(object):
    SIMID = "simID"
    SIMNAME = "simName"
    RIDER = "rider"
    ENVIR = "envir"
    MODEL = "model"
    RIDERLIST = "riderList"
    ENVIRLIST = "envirList"
    POWERPLAN = "powerPlan"

# these rely on the above constants to ensure compatibility
class IPCalcAttributes(object):
    CDA = RiderAttributes.CDA
    AIRDENSITY = EnvirAttributes.AIRDENSITY
    MASSKG = RiderAttributes.WEIGHT
    CRR = EnvirAttributes.CRR
    MECHLOSSES = EnvirAttributes.MECHLOSSES
    POWERPLAN = SimAttributes.POWERPLAN
    MAXFORCE = "maxForce"
    RACEDISTANCE = "raceDistance"
    DT = "dt"
    V0 = "v0"
