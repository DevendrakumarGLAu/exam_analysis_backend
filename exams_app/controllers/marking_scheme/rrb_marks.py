class RRBMarks:
    @staticmethod
    def calculate_marks(correct: int, wrong: int, not_attempted: int,exam_type:str):
        marking_scheme = {
            "rrb_constable": {"correct": 1, "wrong": 0.33},  # CGL: +2 for correct, -0.5 for wrong
            "ssc_mts": {"correct": 3, "wrong": 1},    # MTS: +3 for correct, -1 for wrong
            "ssc_gd": {"correct": 1, "wrong": 0.25},  # SSC GD: +1 for correct, -0.25 for wrong
            "ssc-cgl-II": {"correct": 3, "wrong": 1},  # SSC CGGL MAINS: +3 for correct, -1 for wrong
        }
        
        # ✅ Get marking values based on `exam_type`, default to CGL if not found
        scheme = marking_scheme.get(exam_type.lower(), marking_scheme["ssc_gd"])
        
        # ✅ Calculate marks using selected marking scheme
        correct_marks = correct * scheme["correct"]
        wrong_marks = wrong * scheme["wrong"]
        unattempted_marks = 0  # ⚪ No marks for unattempted questions
        
        # ✅ Return total marks for the section
        return correct_marks - wrong_marks + unattempted_marks
