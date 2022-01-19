consort_script = """
flowchart TB
    0(Enrollment)
    1["Assessed for Eligibility (n=287)"]
    p1[ ]
    2["Randomized (n=201)"]
    3["Excluded (n=86) <br> • Not meeting inclusion criteria (n=83) <br> • Declined to participate (n=3) <br> • Other reason (n=0)"]
    p2[ ]
    4(Allocation)
    5["Allocated to intervention (n=101)"]
    6["Allocated to control (n=99)"]
    
    1 --- p1
    p1 --> 2
    p1 --> 3
    2 --> p2
    p2 --> 5
    p2 --- 4
    p2 --> 6

    linkStyle 5 stroke-width:0px
    style 3 text-align:left
    style p1 width:0px
    style p2 width:0px
"""