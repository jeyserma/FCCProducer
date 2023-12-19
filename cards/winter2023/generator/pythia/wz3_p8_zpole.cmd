

! Vertex smearing :
Beams:allowVertexSpread = on
Beams:sigmaVertexX = 5.96e-3   
Beams:sigmaVertexY = 23.8E-6 
Beams:sigmaVertexZ = 0.397     
Beams:sigmaTime = 10.89    !  36.3 ps

! switch off some checks which break when including BES/ISR
Check:epTolErr = 1   
Check:mTolErr = 1   ! necessary for xing
LesHouches:matchInOut = off
Check:history = off ! necessary for BES in Whizard3 


