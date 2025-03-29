from bs4 import BeautifulSoup
import requests

from exams_app.controllers.marking_scheme.sscCGL import SSCCGLMarks

class SSCExamController:
    @staticmethod
    def fetch_ssc_exam_data(url: str, category: str, horizontal_category: str, exam_language: str, exam_type: str, password: str):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Referer": "https://rrb.digialm.com/",
            "Accept-Language": "en-US,en;q=0.9",
        }

        session = requests.Session()  # Create a session
        session.headers.update(headers)
            
        try:
            session.get("https://rrb.digialm.com/") 
            response = session.get(url)
            if response.status_code == 403:
                return {"error": "Access forbidden. The website is blocking this request."}
            elif response.status_code != 200:
                return {"error": f"Request failed: {response.status_code} {response.reason}"}

            response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)

            soup = BeautifulSoup(response.text, "html.parser")

            exam_title_tag = soup.find("span", style=lambda value: value and "font-size:22px" in value)
            exam_title = exam_title_tag.text.strip() if exam_title_tag else "N/A"

            # Extract Exam Details from the Table
            table = soup.find("table", {"border": "1"})
            exam_data = {}

            if table:
                for row in table.find_all("tr"):
                    columns = row.find_all("td")
                    if len(columns) == 2:  # Ensure key-value pairs exist
                        key = columns[0].get_text(strip=True) if columns[0] else "Unknown"
                        value = columns[1].get_text(strip=True) if columns[1] else "Unknown"
                        exam_data[key] = value

            # Extract Sections
            sections = []
            section_containers = soup.select(".grp-cntnr .section-cntnr")
            for section in section_containers:
                section_label = section.select_one(".section-lbl .bold")
                section_name = section_label.text.strip() if section_label and section_label.text else "Unnamed Section"
                questions = section.select(".question-pnl")
                correct_count = 0
                wrong_count = 0
                not_attempted_count = 0
                
                for question in questions:
                    question_text = question.find('td', class_='bold')
                    chosen_option_tag = question.find('td', text="Chosen Option :")
                    if chosen_option_tag:
                        chosen_option_value = chosen_option_tag.find_next('td').text.strip()
                    else:
                        chosen_option_value = None

                    if chosen_option_value == '--' or not chosen_option_value:
                        chosen_option_number = None
                    else:
                        chosen_option_number = chosen_option_value.split('.')[0].strip()

                    # Extract the correct answer
                    correct_answer_tag = question.find('td', class_='rightAns')
                    correct_answer_value = correct_answer_tag.get_text(strip=True) if correct_answer_tag else None
                    correct_answer_number = correct_answer_value.split('.')[0].strip() if correct_answer_value else None

                    # Determine correctness
                    if chosen_option_number == correct_answer_number:
                        correct_count += 1  # Correct answer ✅
                    elif chosen_option_number and chosen_option_number != correct_answer_number:
                        wrong_count += 1  # Wrong answer ❌
                    else:
                        not_attempted_count += 1  # Unattempted ❓
                section_marks = SSCCGLMarks.calculate_marks(correct_count, wrong_count, not_attempted_count,exam_type)

                sections.append({
                    "section_name": section_name,
                    "total_questions": len(questions),
                    "correct": correct_count,
                    "wrong": wrong_count,
                    "unattempted": not_attempted_count,
                    "raw_marks": section_marks
                })
            total_marks=0
            if exam_type=="ssc-cgl":
                total_marks = sum(
                    SSCCGLMarks.calculate_marks(section["correct"], section["wrong"], section["unattempted"],exam_type) 
                    for section in sections
                )
            if exam_type=="ssc-cgl-II":
                total_marks = sum(
                    SSCCGLMarks.calculate_marks(section["correct"], section["wrong"], section["unattempted"],exam_type) 
                    for section in sections
                )
            elif exam_type=="ssc_mts":               
                sections = [
                    section for section in sections 
                    if section["section_name"] in ["General Awareness", "English Language and Comprehension"]
                ]
                total_marks = sum(
                    SSCCGLMarks.calculate_marks(section["correct"], section["wrong"], section["unattempted"],exam_type) 
                    for section in sections
                )
            else:
                total_marks = sum(
                    SSCCGLMarks.calculate_marks(section["correct"], section["wrong"], section["unattempted"],exam_type) 
                    for section in sections
                )
                
            # ✅ Filter sections to include only English and General Awareness
                
            total_attempted = sum(section["correct"] + section["wrong"] for section in sections)
            total_unattempted = sum(section["unattempted"] for section in sections)
            total_wrong = sum(section["wrong"] for section in sections)
                            
            extracted_data = {
                "exam_title": exam_title,
                "exam_details": exam_data,
                "sections": sections,
                "total_marks_received": total_marks,
                "total_attempted": total_attempted, 
                "total_unattempted": total_unattempted,
                "total_wrong": total_wrong  
            }

            return extracted_data

        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}

        except Exception as e:
            return {"error": f"An unexpected error occurred: {str(e)}"}