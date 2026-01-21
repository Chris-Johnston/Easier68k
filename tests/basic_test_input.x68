* Equates section
start       EQU $400
testData    EQU $ABCD

* Code section
            ORG start
            MOVE #-3, D0
            MOVE #testData, ($00AAAAAA).L
            LEA magic, A0

            SIMHALT

* Data section
magic       DC.B $AB, $CD

            END start
