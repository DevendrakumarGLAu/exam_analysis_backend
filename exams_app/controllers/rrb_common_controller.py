from bs4 import BeautifulSoup
import requests
from datetime import datetime
import logging
from playwright.sync_api import sync_playwright

from exams_app.controllers.marking_scheme.rrb_marks import RRBMarks
from exams_app.controllers.marking_scheme.sscCGL import SSCCGLMarks
from exams_app.models import Question, RRBNTPCExamResult, RRBSectionResult, SSCCGLExamResult, SectionResult
import traceback
class RRBExamsController:
    def fetch_page_content_with_playwright(url):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, timeout=60000)
                html = page.content()
                browser.close()
                return html
        except Exception as e:
            logging.error(f"Playwright failed to fetch page: {e}")
            logging.error(traceback.format_exc())  # log full traceback
            raise

    def fetch_rrb_exams_data(url: str, category: str, horizontal_category: str,
                        exam_language: str, rrb_zone: str,password:str, exam_type:str):
        print("exam type",exam_type)
        logging.info("Inside fetch_rrb_exams_data()...")
        # headers = {
        #             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        #                         "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        #             "Referer": "https://rrb.digialm.com/",
        #             "Accept-Language": "en-US,en;q=0.9",
        #             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        #             "Connection": "keep-alive",
        #         }

        # session = requests.Session()  # Create a session
        # session.headers.update(headers)
        try:
            logging.info("Sending initial session.get to homepage...")
            print("Sending initial session.get to homepage...")
            # session.get("https://rrb.digialm.com/") 
            logging.info(f"Requesting actual exam URL: {url}")
            print(f"Requesting actual exam URL: {url}")
            # response = session.get(url)
            # logging.info(f"Response status: {response.status_code}")
            # print(f"Response status: {response.status_code}")
            # print("line 31",response.status_code)
            # print("line 32",response.text[:500])
            # if response.status_code == 403:
            #     return {"error": "Access forbidden. The website is blocking this request."}
            # elif response.status_code == 503:
            #     return {"error": "503 Service Unavailable. Likely blocked on Render."}
            # elif response.status_code != 200:
            #     return {"error": f"Request failed: {response.status_code} {response.reason}"}
            
            # response.raise_for_status()
            # print(response.status_code)
            # print(response.text[:500])
            html = RRBExamsController.fetch_page_content_with_playwright(url)
            print("html find")
            soup = BeautifulSoup(html, "html.parser")
            
            # soup = BeautifulSoup(response.text, "html.parser")
            exam_title_tag = soup.find("span", style=lambda value: value and "font-size:22px" in value)
            exam_title = exam_title_tag.text.strip() if exam_title_tag else "N/A"
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
            raw_questions = []
            exam_title = exam_data.get("Subject", "hhh"),
            section_containers = soup.select(".grp-cntnr .section-cntnr")
            for section in section_containers:
                section_label = section.select_one(".section-lbl .bold")
                section_name = section_label.text.strip() if section_label and section_label.text else "Unnamed Section"
                questions = section.select(".question-pnl")
                correct_count = 0
                wrong_count = 0
                not_attempted_count = 0
                
                question_text = ""
                question_number = ""
                tds = soup.find_all("td", class_="bold")
                question_text_part = tds[1]
                for question in questions:
                    if len(tds) >= 2:
                        image_tag = question_text_part.find('img')
                        image_src = image_tag['src'] if image_tag else None
                        question_text = " ".join(question_text_part.stripped_strings)

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
                    
                    # extract question and option
                    option_map = {}
                    option_rows = question.select('tr:has(td.bold:-soup-contains("Ans"))')

                    for row in option_rows:
                        option_cells = row.find_all("td")
                        if len(option_cells) >= 2:
                            raw_option_text = option_cells[1].get_text(strip=True)
                            if '.' in raw_option_text:
                                number, text = raw_option_text.split('.', 1)
                                option_map[number.strip()] = text.strip()
                    option_keys = sorted(option_map.keys())  # usually ["1", "2", "3", "4"]
                    option_a = option_map.get(option_keys[0], "") if len(option_keys) > 0 else ""
                    option_b = option_map.get(option_keys[1], "") if len(option_keys) > 1 else ""
                    option_c = option_map.get(option_keys[2], "") if len(option_keys) > 2 else ""
                    option_d = option_map.get(option_keys[3], "") if len(option_keys) > 3 else ""

                    # Determine correctness
                    is_correct = False
                    if chosen_option_number == correct_answer_number:
                        correct_count += 1  # Correct answer ✅
                        is_correct = True
                    elif chosen_option_number and chosen_option_number != correct_answer_number:
                        wrong_count += 1  # Wrong answer ❌
                        is_correct = False
                    else:
                        not_attempted_count += 1  # Unattempted ❓
                        is_correct = False
                        
                    raw_questions.append({
                        "question_text": question_text,
                        "option_a": option_a,
                        "option_b": option_b,
                        "option_c": option_c,
                        "option_d": option_d,
                        "chosen_option_number": chosen_option_number,
                        "correct_answer_number": correct_answer_number,
                        "is_correct": is_correct,
                    })
                section_marks = RRBMarks.calculate_marks(correct_count, wrong_count, not_attempted_count,exam_type)

                sections.append({
                    "section_name": section_name,
                    "total_questions": len(questions),
                    "correct": correct_count,
                    "wrong": wrong_count,
                    "unattempted": not_attempted_count,
                    "raw_marks": section_marks
                })
                for q in raw_questions:
                    Question.objects.create(
                        section_name=section_name,
                        question_text=q["question_text"],
                        option_a=q["option_a"],
                        option_b=q["option_b"],
                        option_c=q["option_c"],
                        option_d=q["option_d"],
                        chosen_option=q["chosen_option_number"],
                        correct_option=q["correct_answer_number"],
                        is_correct=q["is_correct"]
                    )
            total_marks=0
            if exam_type=="rrb-ntpc-stage-1":
                total_marks = sum(
                    RRBMarks.calculate_marks(section["correct"], section["wrong"], section["unattempted"],exam_type) 
                    for section in sections
                )
                exam_date_str = exam_data.get("Exam Date", "01/01/2000")
                try:
                    exam_date = datetime.strptime(exam_date_str,"%d/%m/%Y").date()
                except ValueError:
                    exam_date = None
                print("rrb zones",rrb_zone)
                exam_result , created = RRBNTPCExamResult.objects.update_or_create(
                    roll_number=exam_data.get("Roll Number", "Unknown"),
                    defaults={
                        "candidate_name": exam_data.get("Candidate Name", "Unknown"),
                        "venue_name": exam_data.get("Test Centre Name", "Unknown"),
                         "exam_date": exam_date,
                         "exam_time": exam_data.get("Test Time", "Unknown"),
                         "category": category,
                          "rrb_zone": rrb_zone,
                         "horizontal_category": horizontal_category,
                         "language": exam_language,
                         "url": url,
                         "subject": exam_data.get("Subject", "Unknown"),
                         "total_marks_received": total_marks,
                        "total_attempted": sum(s["correct"] + s["wrong"] for s in sections),
                        "total_unattempted": sum(s["unattempted"] for s in sections),
                        "total_wrong": sum(s["wrong"] for s in sections),
                    }
                )
                exam_result.sections.all().delete()
                
                for section in sections:
                    RRBSectionResult.objects.create(
                        exam_result=exam_result,
                        section_name=section["section_name"],
                        total_questions=section["total_questions"],
                        correct=section["correct"],
                        wrong=section["wrong"],
                        unattempted=section["unattempted"],
                        raw_marks=section["raw_marks"]
                    )

                # return {"success": f"Exam data for {exam_result.candidate_name} saved successfully!"}
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
        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return {"error": f"An unexpected error occurred in {exam_type}: {str(e)}"}

