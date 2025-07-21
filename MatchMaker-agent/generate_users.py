import json
import random

# Lists for generating random data
names = ["Ahmed", "Ayesha", "Bilal", "Fatima", "Hassan", "Zainab", "Usman", "Sana", "Omar", "Hina", 
         "Ali", "Maryam", "Khalid", "Nadia", "Tahir", "Amna", "Saad", "Rabia", "Faisal", "Zara", 
         "Imran", "Saba", "Yousuf", "Aisha", "Hamza", "Iqra", "Asad", "Maha", "Waqas", "Hafsa"]
surnames = ["Khan", "Siddiqui", "Ahmed", "Zafar", "Raza", "Malik", "Qureshi", "Iqbal", "Farooq", "Yasir",
            "Rehman", "Nawaz", "Mehmood", "Sheikh", "Abbas", "Basri", "Javed", "Shah", "Ali", "Saeed"]
locations = ["Karachi", "Lahore", "Islamabad", "Rawalpindi", "Faisalabad", "Peshawar", "Quetta", "Multan"]
educations = ["High School", "Bachelor's", "Master's", "PhD", "Other"]
genders = ["male", "female"]

# Generate 500 user records
users = []
for _ in range(500):
    user = {
        "name": f"{random.choice(names)} {random.choice(surnames)}",
        "age": random.randint(18, 50),
        "gender": random.choice(genders),
        "location": random.choice(locations),
        "education": random.choice(educations)
    }
    users.append(user)

# Save to users.json
with open("users.json", "w") as file:
    json.dump(users, file, indent=4)

print("Generated users.json with 500 records.")