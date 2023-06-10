set io_facs [list] 
lappend io_facs "tb_inverter.inverter.A"
lappend io_facs "tb_inverter.inverter.Z" 
lappend io_facs "tb_inverter.clock"
gtkwave::addSignalsFromList $io_facs 
gtkwave::/Time/Zoom/Zoom_Full
                
