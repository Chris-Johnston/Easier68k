* Equates section
start       EQU $400
testData    EQU $ABCD

* Code section
            ORG start
            MOVE #testData, D0
            LEA magic, A0

            SIMHALT

* Data section
magic       DC.B $AB, $CD

            END start
