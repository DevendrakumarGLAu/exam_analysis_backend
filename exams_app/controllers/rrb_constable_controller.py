import requests
from bs4 import BeautifulSoup
from exams_app.controllers.marking_scheme.rrb_marks import RRBMarks

class RRBConstableController:
    @staticmethod
    def fetch_exam_data(url: str, category: str, horizontal_category: str,
                        exam_language: str, rrb_zone: str, password: str, exam_type: str):
        """
        Function to scrape data from the given URL.
        This function fetches the HTML content of the URL and extracts the required exam data.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            "Referer": "https://rrb.digialm.com/",
            "Accept-Language": "en-US,en;q=0.9",
        }

        session = requests.Session()  # Create a session
        session.headers.update(headers)
        try:
        #     headers = {
        #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        #     "Referer": "https://rrb.digialm.com/",  # This tells the site where the request is coming from
        #     "Accept-Language": "en-US,en;q=0.9",
        # }
            # response = requests.get(url)
            # session = requests.Session()
            # session.headers.update(headers)
            session.get("https://rrb.digialm.com/")  
            response = session.get(url)
            if response.status_code == 403:
                return {"error": "Access forbidden. The website is blocking this request."}
            elif response.status_code != 200:
                return {"error": f"Request failed: {response.status_code} {response.reason}"}

            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Extract Exam Details Table
                table = soup.find('table', {'border': '1'})
                exam_data = {}

                if table:
                    rows = table.find_all('tr')
                    for row in rows:
                        columns = row.find_all('td')
                        if len(columns) > 1:  # Ensure the row contains key-value columns
                            key = columns[0].get_text(strip=True)
                            value = columns[1].get_text(strip=True)
                            exam_data[key] = value
                
                exam_title = exam_data.get('Exam Title', exam_data.get('Exam Name', 'N/A'))  # Look for 'Exam Name' if 'Exam Title' isn't found
                # Extract Sections: Find all section containers or labels
                sections = []  # List to store section-wise data
                section_containers = soup.select(".section-cntnr")  # Adjust the selector as per your HTML
                overall_correct_count = 0
                overall_wrong_count = 0
                overall_not_attempted_count = 0
                overall_raw_marks = 0 

                for section in section_containers:
                    # Extract the section name (assuming it's within an element with a specific class or tag)
                    section_name_tag = section.select_one(".section-lbl .bold")  # Adjust the selector as needed
                    section_name = section_name_tag.text.strip() if section_name_tag else "Unnamed Section"

                    # Extract questions within this section
                    questions = section.select(".question-pnl")  # Adjust this selector if necessary
                    
                    correct_count = 0
                    wrong_count = 0
                    not_attempted_count = 0

                    # Evaluate each question in this section
                    for question in questions:
                        chosen_option_tag = question.find('td', text="Chosen Option :")
                        if chosen_option_tag:
                            chosen_option_value = chosen_option_tag.find_next('td').text.strip()
                        else:
                            chosen_option_value = None
                        
                        if chosen_option_value == '--' or not chosen_option_value:
                            chosen_option_number = None
                        else:
                            chosen_option_number = chosen_option_value.split('.')[0].strip()

                        correct_answer_tag = question.find('td', class_='rightAns')
                        if correct_answer_tag:
                            correct_answer_value = correct_answer_tag.get_text(strip=True)
                        else:
                            correct_answer_value = None
                        
                        correct_answer_number = correct_answer_value.split('.')[0].strip() if correct_answer_value else None

                        # Determine correctness of the answer
                        if chosen_option_number == correct_answer_number:
                            correct_count += 1
                        elif chosen_option_number and chosen_option_number != correct_answer_number:  # Incorrect answer
                            wrong_count += 1
                        else:
                            not_attempted_count += 1  # Unattempted question

                    # Calculate section marks using the provided marking scheme
                    section_marks = RRBMarks.calculate_marks(correct_count, wrong_count, not_attempted_count, exam_type)

                    sections.append({
                        "section_name": section_name,  # Dynamic section name from HTML
                        "total_questions": len(questions),
                        "correct": correct_count,
                        "wrong": wrong_count,
                        "unattempted": not_attempted_count,
                        "raw_marks": section_marks
                    })

                    overall_correct_count += correct_count
                    overall_wrong_count += wrong_count
                    overall_not_attempted_count += not_attempted_count
                    overall_raw_marks += section_marks

                sections.append({
                "section_name": "Overall",
                "total_questions": sum(section["total_questions"] for section in sections),
                "correct": overall_correct_count,
                "wrong": overall_wrong_count,
                "unattempted": overall_not_attempted_count,
                "raw_marks": overall_raw_marks
            })
                total_marks = overall_raw_marks

                # Calculate Total Marks
                # total_marks = sum(
                #     RRBMarks.calculate_marks(section["correct"], section["wrong"], section["unattempted"], exam_type) 
                #     for section in sections
                # )

                # Calculate Total Attempted, Unattempted, and Wrong Counts
                total_attempted = sum(section["correct"] + section["wrong"] for section in sections if section["section_name"] != "Overall")
                total_unattempted = sum(section["unattempted"] for section in sections if section["section_name"] != "Overall")
                total_wrong = sum(section["wrong"] for section in sections if section["section_name"] != "Overall")


                # Constructing the final response
                extracted_data = {
                    "exam_title": exam_title,  # You can modify this to extract exam title correctly
                    "exam_details": exam_data,
                    "sections": sections,
                    "total_marks_received": total_marks,
                    "total_attempted": total_attempted,
                    "total_unattempted": total_unattempted,
                    "total_wrong": total_wrong
                }

                return extracted_data
            
            else:
                return {"error": f"Failed to retrieve content. Status Code: {response.status_code}"}
        
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}
