from typing import List
from pydantic import BaseModel


class HashableBaseModel(BaseModel):
    def __hash__(self):
        return hash((type(self),) + tuple(self.__dict__.values()))


class Filament(HashableBaseModel):
    bed_temperature: float = 60
    extruder_temperature: float = 200
    fan_speed: float = 255


class Extruder(HashableBaseModel):
    volumetric_flow_mm3s: float = 7
    """ How fast can this extruder push plastic through the nozzle.
    
    A normal V6 is ~7mm3/s for PLA
    A volcano is ~15mm3/s for PLA

    Flexable filaments can be quite low, around the 1mm/s range. 
    
    CHT nozzles, running at higher temperatures, more powerful heaters and longer
    melt zones all increase the volumetric flow rate.
    """

    filament_diameter_mm: float = 1.75
    """ What diameter filament is this extruder designed for. """

    filament: Filament = Filament()
    """ What filamet is loaded into this extruder. """

    safe_angle_from_nozzle_degrees: float = 15
    """
    When printing in a non-planer manner, there should be no part of the print higher than a cone of this angle. If it is set to
    zero, then the print will be planar. If it is set to 90, then the printer can put plastic anywhere.
    """

    nozzle_diameter_mm: float = 0.4
    """ The diameter of the orifice in the nozzle that this extruder uses. """



class PrinterMechanical(HashableBaseModel):
    print_bed_surface: str = "Bed.stl"
    """ The bed surface that the printer will print on. Normally this is flat """

    print_volume_height_mm: float = 200
    """ How high above the bed can the printer print. """

    max_print_feedrate_mm_s: float = 100
    """ How fast can the printer move while extruding plastic """

    max_travel_feedrate_mm_s: float = 500
    """ How fast can the printer physically move it's print head """

    extruders: tuple[Extruder] = (Extruder(),)



class Slicer(HashableBaseModel):

    layer_height_mm: float = 0.3
    """ TBH I'd like to nuke this parameter. It seems like something that the 
    machine should be able to determine based on desired surface quality and the 
    nozzle size. But it is a very handy number to adjust until we have file formats
    that can represent surface quality all the way from CAD. """


class Configuration(HashableBaseModel):
    
    printer: PrinterMechanical = PrinterMechanical()
    slicer: Slicer = Slicer()


