"""
Valid attributes for Rider, Environment, Simulation, and IPCalculator.
Model and View are dependent on this, instead of being dependent on each other
"""

class RiderAttributes(object):
    RIDERID = "riderID"
    FIRSTNAME = "firstName"
    LASTNAME = "lastName"
    WEIGHT = "massKG"   # TODO this is misleading and needs to be renamed
    FTP = "FTP"
    WPRIME = "wPrime"
    CDA = "CdA"
    POWERRESULTS = "powerResults"

    @classmethod
    def set(cls):
        return {cls.RIDERID,
                cls.FIRSTNAME,
                cls.LASTNAME,
                cls.WEIGHT,
                cls.FTP,
                cls.WPRIME,
                cls.CDA,
                cls.POWERRESULTS}

class EnvirAttributes(object):
    ENVIRID = "envirID"
    ENVIRNAME = "envirName"
    AIRDENSITY = "airDensity"
    CRR = "Crr"
    MECHLOSSES = "mechLosses"

    @classmethod
    def set(cls):
        return {cls.ENVIRID,
                 cls.ENVIRNAME,
                cls.AIRDENSITY,
                cls.CRR,
                cls.MECHLOSSES}

class SimAttributes(object):
    SIMID = "simID"
    SIMNAME = "simName"
    RIDER = "rider"
    ENVIR = "envir"
    MODEL = "model"
    RIDERLIST = "riderList"
    ENVIRLIST = "envirList"
    POWERPLAN = "powerPlan"

    @classmethod
    def set(cls):
        return {cls.SIMID,
                cls.SIMNAME,
                cls.RIDER,
                cls.ENVIR,
                cls.MODEL,
                cls.RIDERLIST,
                cls.ENVIRLIST,
                cls.POWERPLAN}

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

    @classmethod
    def set(cls):
        return {cls.CDA,
                cls.AIRDENSITY,
                cls.MASSKG,
                cls.CRR,
                cls.MECHLOSSES,
                cls.POWERPLAN,
                cls.MAXFORCE,
                cls.RACEDISTANCE,
                cls.DT,
                cls.V0}
