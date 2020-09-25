#https://stackoverflow.com/questions/55713024/why-is-b-x02-not-the-same-as-the-value-2-or-int2-in-python
#https://www.ascii-code.com/

StartTransmissionCharacter = "\x02" #ASCII code for hex 02, or STX
EndTransmissionCharacter = "\x03" #ASCII for hex 03, or ETX

# StartTransmissionCharacter = "\x32" #ASCII for the digit "2"
# EndTransmissionCharacter = "\x33" #ASCII for the digit "3"


#Data Message Types
NewContainer = "ADDCONTA"
ContainerComplete = "CONTCOMP"
AssignmentComplete = "ASGNCOMP"
OrderComplete = "ORDRCOMP"
RouteComplete = "ROUTCOMP"

