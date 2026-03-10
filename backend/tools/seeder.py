import asyncio
import argparse
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import select, delete

from app.database import async_session_maker, engine, Base
from app.models import User, ClaimInsurance, ClaimReview, ClaimApproval, Insurance


from app.utils.security import hash_password

from .seeder_data import SEED_USERS, SEED_INSURANCES

async def clear_all():
    """Clear all data in correct order (respecting foreign keys)"""
    async with async_session_maker() as session:
        await session.execute(delete(ClaimApproval))
        await session.execute(delete(ClaimReview))
        await session.execute(delete(ClaimInsurance))
        await session.execute(delete(Insurance))
        await session.execute(delete(User))
        await session.commit()
        print("Cleared all data")


async def seed_insurances():
    """Seed insurance data"""
    async with async_session_maker() as session:
        for insurance_data in SEED_INSURANCES:
            # Check if insurance already exists (by number)
            result = await session.execute(
                select(Insurance).where(Insurance.number == insurance_data["number"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                print(f"  → Insurance {insurance_data['number']} already exists")
                continue

            insurance = Insurance(**insurance_data)
            session.add(insurance)
            print(f"   Created insurance: {insurance_data['number']} ({insurance_data['title']})")

        await session.commit()


async def seed_users() -> dict[str, User]:
    """Seed users and return a dict mapping email to User object"""
    users_map = {}
    async with async_session_maker() as session:
        for user_data in SEED_USERS:
            # Check if user already exists
            result = await session.execute(
                select(User).where(User.email == user_data["email"])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"  → User {user_data['email']} already exists")
                users_map[user_data["email"]] = existing
                continue
            
            user = User(
                email=user_data["email"],
                username=user_data["username"],
                hashed_password=hash_password(user_data["password"]),
                role=user_data["role"],
            )
            session.add(user)
            await session.flush()  # Get the ID
            users_map[user_data["email"]] = user
            print(f"   Created user: {user_data['email']} ({user_data['role'].value})")
        await session.commit()
        
        # Refresh to get IDs for all users
        for email in users_map:
            result = await session.execute(
                select(User).where(User.email == email)
            )
            users_map[email] = result.scalar_one()
    
    return users_map


async def run_seeder(clear: bool = False):
    print("\nDatabase Seeder")
    print("=" * 40)
    
    if clear:
        print("\nClearing existing data...")
        await clear_all()

    print("\nSeeding insurances...")
    await seed_insurances()
    
    print("\nSeeding users...")
    await seed_users()
    
    print("\n" + "=" * 40)
    print("Seeding complete!\n")
    
    # Print credentials
    print("-" * 40)
    for user_data in SEED_USERS:
        print(f"  {user_data['role'].value:10} | {user_data['email']:25} | {user_data['password']}")

    print("-" * 60)
    for ins in SEED_INSURANCES:
        print(f"  {ins['number']:13} | {ins['title']}")
    print()
 

def main():
    parser = argparse.ArgumentParser(description="Database seeder")
    parser.add_argument(
        "--clear", "-c",
        action="store_true",
        help="Clear existing data before seeding"
    )
    args = parser.parse_args()
    
    asyncio.run(run_seeder(clear=args.clear))


if __name__ == "__main__":
    main()
