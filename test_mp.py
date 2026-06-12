import sys
import os

print("Python version:", sys.version)
print("Python path:", sys.path)

try:
    import mediapipe as mp
    print("Mediapipe imported successfully.")
    print("Attributes in mp:", dir(mp))
    print("Solutions attribute:", hasattr(mp, "solutions"))
    if hasattr(mp, "solutions"):
        print("Solutions dir:", dir(mp.solutions))
except Exception as e:
    print("Error importing mediapipe:", e)
