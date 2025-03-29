from bs4 import BeautifulSoup
import requests

class RRBJEController:
    @staticmethod
    def fetch_exam_data(url: str, category: str, horizontal_category: str,
                        exam_language: str, rrb_zone: str, rrb_branch: str):
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
            session.get("https://rrb.digialm.com/") 
            response = session.get(url)  
            response = session.get(url)
            if response.status_code == 403:
                return {"error": "Access forbidden. The website is blocking this request."}
            elif response.status_code != 200:
                return {"error": f"Request failed: {response.status_code} {response.reason}"}

            # response = requests.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                
                table = soup.find('table', {'border': '1'})
                if table:
                    rows = table.find_all('tr')
                    exam_data = {}
                    
                    for row in rows:
                        columns = row.find_all('td')
                        if len(columns) > 1:  # Check if there are at least two columns in the row
                            key = columns[0].get_text(strip=True)
                            value = columns[1].get_text(strip=True)
                            exam_data[key] = value
                    
                    # Extract the questions and answers section
                    questions = soup.find_all('div', class_='question-pnl')
                    correct_count = 0
                    wrong_count = 0
                    not_attempted_count = 0
                    
                    for question in questions:
                        question_data = {}
                        question_text = question.find('td', class_='bold')
                        if question_text:
                            question_data['question'] = question_text.text.strip()

                        # Extract the answer choices and check if the user has selected an option
                        chosen_option_tag = question.find('td', text="Chosen Option :")
                        if chosen_option_tag:
                            chosen_option_value = chosen_option_tag.find_next('td').text.strip()
                        else:
                            chosen_option_value = None
                        if chosen_option_value == '--' or not chosen_option_value:
                            chosen_option_number = None
                        else:
                            chosen_option_number = chosen_option_value.split('.')[0].strip() if chosen_option_value else None
                        correct_answer_tag = question.find('td', class_='rightAns')
                        if correct_answer_tag:
                            correct_answer_value = correct_answer_tag.get_text(strip=True)
                        else:
                            correct_answer_value = None
                        correct_answer_number = correct_answer_value.split('.')[0].strip() if correct_answer_value else None
                        
                        if chosen_option_number == correct_answer_number:
                            correct_count += 1
                        elif chosen_option_number and chosen_option_number != correct_answer_number:  # If the answer was chosen but incorrect
                            wrong_count += 1
                        else:
                            not_attempted_count += 1
                    marks_per_correct_answer = 1
                    negative_mark_per_wrong_answer = marks_per_correct_answer / 3
                    actual_marks = (correct_count * marks_per_correct_answer) - (wrong_count * negative_mark_per_wrong_answer)
                    
                    extracted_data = {
                        'exam_data': exam_data,
                        'right_answers': correct_count,
                        'wrong_answers': wrong_count,
                        'not_attempted': not_attempted_count,
                        'actual_marks': round(actual_marks, 3)
                    }
                    return extracted_data
                else:
                    return {"error": "Exam details table not found."}
            else:
                return {"error": f"Failed to retrieve content. Status Code: {response.status_code}"}
        
        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}
