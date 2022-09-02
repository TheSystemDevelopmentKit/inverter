# SPDX-License-Identifier: Apache-2.0

# Delete previous signals on display
gtkwave::/Edit/Highlight_All
gtkwave::/Edit/Delete

# Global signals
set sig_idx 0
set alias_idx 1
set radix_idx 2
set tfile_idx 3
set tfile_path /TranslateFiles/
variable tcl_path [file normalize [info script]]

#### Procedure definitions ####

# Returns path of the tcl script
proc getResourceDirectory {} {
  variable tcl_path
  return [file dirname $tcl_path]
}

# Reloads this Tcl
proc reloadTcl {} {
  global tcl_path
  gtkwave::/File/Read_Tcl_Script_File $tcl_path
}

# Adds a signal list
# Arguments: signal list, color, name for comment trace
proc add_signal_list { sig_list color {topic ""} } {
  global sig_idx
  global alias_idx
  global radix_idx
  global tfile_idx
  global tfile_path
  upvar $sig_list x
  # Add a comment trace if there is one
  if {[string length $topic] != 0} {
    gtkwave::addCommentTracesFromList [list "$topic"]
  }
  foreach signal $x {
    set temp_list [ list ]
    lappend temp_list [lindex $signal $sig_idx]
    gtkwave::addSignalsFromList $temp_list
    gtkwave::highlightSignalsFromList $temp_list
    gtkwave::/Edit/Color_Format/$color
    # Rename the signal if an alias was provided
    if {[string length {lindex $signal $alias_idx}] != 0} {
      gtkwave::/Edit/Alias_Highlighted_Trace [lindex $signal $alias_idx]
      # Needs a re-highlight as the signal name changes
      gtkwave::highlightSignalsFromList [list [lindex $signal $alias_idx]]
    }
    # Set data format
    if {[lindex $signal $radix_idx] ne ""} {
      gtkwave::/Edit/Data_Format/[lindex $signal $radix_idx]
    }
    # Set translation filter file
    if {[lindex $signal $tfile_idx] ne ""} {
      set which_f [ gtkwave::setCurrentTranslateFile [getResourceDirectory]$tfile_path[lindex $signal $tfile_idx]]
      gtkwave::installFileFilter $which_f
    }
  }
}

#### Signals ####
# Signal bundles are defined here
# Note that they must still be added to gtkwave with 'add_signal_list' command (see end of file)
#
# On each row:
# First element is name of the signal
# Second element is the alias (how you want it to be displayed in gtkwave)
# Third element is the radix (data format (Binary, Decimal, Hex, ASCII etc.))
# Fourth element is the name of a (possible) Translate File (Stored in ./TranslateFiles/)
#
# After first element, the rest are optional. However, if you want to define fourth element,
# you must also define second and third.
# Note that, when providing a translate file, you should provide a radix that matches with the radix
# used in the translate file

set io_facs [list] 
lappend io_facs "tb_inverter.inverter.A"
lappend io_facs "tb_inverter.inverter.Z" 
lappend io_facs "tb_inverter.clock"
gtkwave::addSignalsFromList $io_facs 

gtkwave::/Edit/UnHighlight_All
gtkwave::/Time/Zoom/Zoom_Full
