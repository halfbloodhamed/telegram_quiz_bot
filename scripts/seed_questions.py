import asyncio
import sys
sys.path.insert(0, ".")

from app.database.connection import get_db
from app.database.repositories.question_repository import QuestionRepository, CategoryRepository
from app.database.models import DifficultyLevel


QUESTIONS = [
    # Programming
    {"category": "Programming", "text": "What does HTML stand for?", "a": "Hyper Text Markup Language", "b": "High Tech Modern Language", "c": "Home Tool Markup Language", "d": "Hyperlinks and Text Markup Language", "correct": "A", "difficulty": "EASY"},
    {"category": "Programming", "text": "Which programming language is known as the 'language of the web'?", "a": "Python", "b": "JavaScript", "c": "Java", "d": "C++", "correct": "B", "difficulty": "EASY"},
    {"category": "Programming", "text": "What is the time complexity of binary search?", "a": "O(n)", "b": "O(log n)", "c": "O(n²)", "d": "O(1)", "correct": "B", "difficulty": "MEDIUM"},
    {"category": "Programming", "text": "Which data structure uses LIFO?", "a": "Queue", "b": "Array", "c": "Stack", "d": "Tree", "correct": "C", "difficulty": "EASY"},
    {"category": "Programming", "text": "What does SQL stand for?", "a": "Structured Query Language", "b": "Simple Question Language", "c": "Structured Question Language", "d": "Simple Query Language", "correct": "A", "difficulty": "EASY"},
    
    # Science
    {"category": "Science", "text": "What is the chemical symbol for gold?", "a": "Go", "b": "Gd", "c": "Au", "d": "Ag", "correct": "C", "difficulty": "MEDIUM"},
    {"category": "Science", "text": "How many planets are in our solar system?", "a": "7", "b": "8", "c": "9", "d": "10", "correct": "B", "difficulty": "EASY"},
    {"category": "Science", "text": "What is the speed of light?", "a": "300,000 km/s", "b": "150,000 km/s", "c": "500,000 km/s", "d": "200,000 km/s", "correct": "A", "difficulty": "MEDIUM"},
    {"category": "Science", "text": "What is H2O?", "a": "Oxygen", "b": "Hydrogen", "c": "Water", "d": "Carbon Dioxide", "correct": "C", "difficulty": "EASY"},
    {"category": "Science", "text": "Who developed the theory of relativity?", "a": "Isaac Newton", "b": "Albert Einstein", "c": "Stephen Hawking", "d": "Nikola Tesla", "correct": "B", "difficulty": "MEDIUM"},
    
    # History
    {"category": "History", "text": "In which year did World War II end?", "a": "1943", "b": "1944", "c": "1945", "d": "1946", "correct": "C", "difficulty": "MEDIUM"},
    {"category": "History", "text": "Who was the first President of the United States?", "a": "Thomas Jefferson", "b": "George Washington", "c": "John Adams", "d": "Benjamin Franklin", "correct": "B", "difficulty": "EASY"},
    {"category": "History", "text": "When did the Berlin Wall fall?", "a": "1987", "b": "1988", "c": "1989", "d": "1990", "correct": "C", "difficulty": "MEDIUM"},
    {"category": "History", "text": "Which ancient wonder is still standing?", "a": "Hanging Gardens of Babylon", "b": "Colossus of Rhodes", "c": "Great Pyramid of Giza", "d": "Lighthouse of Alexandria", "correct": "C", "difficulty": "MEDIUM"},
    {"category": "History", "text": "Who painted the Mona Lisa?", "a": "Vincent van Gogh", "b": "Pablo Picasso", "c": "Leonardo da Vinci", "d": "Michelangelo", "correct": "C", "difficulty": "EASY"},
]

# Add more questions
QUESTIONS.extend([
    # Sports
    {"category": "Sports", "text": "How many players are on a soccer team?", "a": "9", "b": "10", "c": "11", "d": "12", "correct": "C", "difficulty": "EASY"},
    {"category": "Sports", "text": "Which country won the 2018 FIFA World Cup?", "a": "Brazil", "b": "Germany", "c": "France", "d": "Argentina", "correct": "C", "difficulty": "MEDIUM"},
    {"category": "Sports", "text": "What is the diameter of a basketball hoop?", "a": "16 inches", "b": "18 inches", "c": "20 inches", "d": "22 inches", "correct": "B", "difficulty": "HARD"},
    
    # Movies
    {"category": "Movies", "text": "Who directed Titanic?", "a": "Steven Spielberg", "b": "James Cameron", "c": "Christopher Nolan", "d": "Martin Scorsese", "correct": "B", "difficulty": "MEDIUM"},
    {"category": "Movies", "text": "Which movie won the first Academy Award for Best Picture?", "a": "Wings", "b": "Sunrise", "c": "The Jazz Singer", "d": "7th Heaven", "correct": "A", "difficulty": "HARD"},
])


async def seed_questions():
    """Seed the database with questions"""
    async for session in get_db():
        question_repo = QuestionRepository(session)
        category_repo = CategoryRepository(session)
        
        # Create categories
        categories = {}
        for cat_name in ["Programming", "Science", "History", "Sports", "Movies"]:
            cat = await category_repo.get_by_name(cat_name)
            if not cat:
                cat = await category_repo.create(cat_name)
            categories[cat_name] = cat.id
        
        await session.commit()
        
        # Add questions
        for q in QUESTIONS:
            category_id = categories.get(q["category"])
            difficulty = DifficultyLevel[q["difficulty"]]
            
            await question_repo.create(
                text=q["text"],
                option_a=q["a"],
                option_b=q["b"],
                option_c=q["c"],
                option_d=q["d"],
                correct_answer=q["correct"],
                category_id=category_id,
                difficulty=difficulty
            )
        
        await session.commit()
        print(f"✅ Successfully seeded {len(QUESTIONS)} questions!")


if __name__ == "__main__":
    asyncio.run(seed_questions())
