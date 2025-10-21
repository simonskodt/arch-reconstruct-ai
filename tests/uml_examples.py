"""Shared test constants"""

# Test data for parameterized tests
UML_DIAGRAMS = [
    # Basic sequence diagram
    ("@startuml Basic\nAlice -> Bob: Hello\nBob --> Alice: Hi\n@enduml",
     "basic_sequence"),

    # Class diagram
    ("@startuml Class\nclass User {\n  +name: String\n  +login()\n}\n@enduml",
     "class_diagram"),

    # Activity diagram
    ("@startuml Activity\nstart\n:Action 1;\nif (condition) then (yes)\n  \
     :Action 2;\nelse (no)\n  :Action 3;\nendif\nstop\n@enduml",
     "activity_diagram"),

    # Use case diagram
    ("@startuml UseCase\n:User: --> (Login)\n:User: --> (View Profile)\n@enduml",
     "use_case_diagram"),
]
