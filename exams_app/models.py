from django.db import models

class SSCCGLExamResult(models.Model):
    roll_number = models.CharField(max_length=50, unique=True)
    candidate_name = models.CharField(max_length=255)
    venue_name = models.CharField(max_length=255)
    exam_date = models.DateField()
    exam_time = models.CharField(max_length=50)
    category = models.CharField(max_length=255)
    horizontal_category = models.CharField(max_length=255, blank=True, null=True)
    language = models.CharField(max_length=100, blank=True, null=True)
    url = models.URLField(max_length=5000)
    subject = models.CharField(max_length=255)
    total_marks_received = models.FloatField()
    total_attempted = models.IntegerField()
    total_unattempted = models.IntegerField()
    total_wrong = models.IntegerField()
    
    def __str__(self):
        return f"{self.candidate_name} - {self.exam_title}"
    
    class Meta:
        db_table = 'ssccglexamresult'
    

class SectionResult(models.Model):
    exam_result = models.ForeignKey(SSCCGLExamResult, related_name='sections', on_delete=models.CASCADE)
    section_name = models.CharField(max_length=255)
    total_questions = models.IntegerField()
    correct = models.IntegerField()
    wrong = models.IntegerField()
    unattempted = models.IntegerField()
    raw_marks = models.FloatField()

    def __str__(self):
        return f"{self.section_name} - {self.exam_result.candidate_name}"
    
    class Meta:
        db_table = 'sectionresult'
    
class Question(models.Model):
    section_name = models.CharField(max_length=255)
    # section = models.ForeignKey('SectionResult', related_name='questions', on_delete=models.CASCADE)
    # question_text = models.TextField(blank=True, null=True)
    question_text = models.TextField()
    question_image = models.URLField(blank=True, null=True)
    option_a = models.TextField(blank=True, null=True)
    option_b = models.TextField(blank=True, null=True)
    option_c = models.TextField(blank=True, null=True)
    option_d = models.TextField(blank=True, null=True)
    chosen_option = models.CharField(max_length=10, blank=True, null=True)
    correct_option = models.CharField(max_length=10, blank=True, null=True)
    is_correct = models.BooleanField(default=False) 
    
    
    class Meta:
        db_table = 'questions'

    def __str__(self):
        return f"Q: {self.question_text[:50]}..."
    
class RRBNTPCExamResult(models.Model):
    roll_number = models.CharField(max_length=50, unique=True)
    candidate_name = models.CharField(max_length=255)
    rrb_zone = models.CharField(max_length=50)
    venue_name = models.CharField(max_length=255)
    exam_date = models.DateField()
    exam_time = models.CharField(max_length=50)
    category = models.CharField(max_length=255)
    horizontal_category = models.CharField(max_length=255, blank=True, null=True)
    language = models.CharField(max_length=100, blank=True, null=True)
    url = models.URLField(max_length=5000)
    subject = models.CharField(max_length=255)
    total_marks_received = models.FloatField()
    total_attempted = models.IntegerField()
    total_unattempted = models.IntegerField()
    total_wrong = models.IntegerField()
    
    def __str__(self):
        return f"{self.candidate_name} - {self.exam_title}"
    
    class Meta:
        db_table = 'rrb_ntpc_examresult'

    

# Create your models here.
