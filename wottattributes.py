"""
Valid attributes for Rider, Environment, and Simulation.
Model and View are dependent on this, instead of being dependent on each other
"""

class RiderAttributes(object):
    RIDERID = "riderID"
    FIRSTNAME = "firstName"
    LASTNAME = "lastName"
    WEIGHT = "weight"
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

class CalcAttributes(object):
    CDA = "CdA"
    AIRDENSITY = "airDensity"
    MASSKG = "massKG"
    CRR = "Crr"
    MECHLOSSES = "mechLosses"
    POWERPLAN = "powerPlan"
    MAXFORCE = "maxForce"
    RACEDISTANCE = "raceDistance"
    DT = "dt"
    V0 = "v0"