from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Question, Category, DifficultyLevel


class QuestionRepository:
    """Question repository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, question_id: int) -> Optional[Question]:
        """Get question by ID"""
        result = await self.session.execute(
            select(Question).where(Question.id == question_id)
        )
        return result.scalar_one_or_none()
    
    async def get_random_questions(
        self,
        count: int,
        exclude_ids: List[int] = None,
        category_id: Optional[int] = None,
        difficulty: Optional[DifficultyLevel] = None
    ) -> List[Question]:
        """Get random questions"""
        query = select(Question)
        
        if exclude_ids:
            query = query.where(Question.id.notin_(exclude_ids))
        
        if category_id is not None:
            query = query.where(Question.category_id == category_id)
        
        if difficulty is not None:
            query = query.where(Question.difficulty == difficulty)
        
        query = query.order_by(func.random()).limit(count)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def create(
        self,
        text: str,
        option_a: str,
        option_b: str,
        option_c: str,
        option_d: str,
        correct_answer: str,
        category_id: Optional[int] = None,
        difficulty: DifficultyLevel = DifficultyLevel.MEDIUM,
        image_url: Optional[str] = None,
        explanation: Optional[str] = None
    ) -> Question:
        """Create new question"""
        question = Question(
            text=text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_answer=correct_answer.upper(),
            category_id=category_id,
            difficulty=difficulty,
            image_url=image_url,
            explanation=explanation
        )
        self.session.add(question)
        await self.session.flush()
        return question
    
    async def delete(self, question: Question):
        """Delete question"""
        await self.session.delete(question)
        await self.session.flush()
    
    async def get_total_questions(self) -> int:
        """Get total number of questions"""
        result = await self.session.execute(
            select(func.count(Question.id))
        )
        return result.scalar_one()


class CategoryRepository:
    """Category repository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, category_id: int) -> Optional[Category]:
        """Get category by ID"""
        result = await self.session.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_name(self, name: str) -> Optional[Category]:
        """Get category by name"""
        result = await self.session.execute(
            select(Category).where(Category.name == name)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[Category]:
        """Get all categories"""
        result = await self.session.execute(select(Category))
        return list(result.scalars().all())
    
    async def create(self, name: str, description: Optional[str] = None) -> Category:
        """Create new category"""
        category = Category(name=name, description=description)
        self.session.add(category)
        await self.session.flush()
        return category
