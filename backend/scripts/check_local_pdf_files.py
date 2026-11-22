import os

files_to_check = [
    'f:/exam/backend/uploads/papers/class-10/cbse10_2024_maths_std.pdf',
    'f:/exam/backend/uploads/papers/cbse-10/cbse_2024_maths_std_paper.pdf',
    'f:/exam/backend/uploads/papers/class-10/cbse10_2023_maths_std.pdf',
    'f:/exam/backend/uploads/papers/cbse-10/cbse_2023_maths_set1.pdf',
    'f:/exam/backend/uploads/papers/cbse-10/cbse_2022_term2_maths.pdf',
    'f:/exam/backend/uploads/papers/cbse-10/cbse_2022_maths_set1.pdf',
    'f:/exam/backend/uploads/papers/cbse-10/cbse_2021_maths_set1.pdf',
    'f:/exam/backend/uploads/papers/cbse-10/cbse_2020_maths_set1.pdf',
    'f:/exam/backend/uploads/papers/cbse-10/cbse_2019_maths_set1.pdf',
    'f:/exam/backend/uploads/papers/cbse-10/cbse_2018_maths_set1.pdf',
    'f:/exam/backend/uploads/papers/cbse-10/cbse_2017_maths_set1.pdf',
    'f:/exam/backend/uploads/papers/cbse-10/cbse_2016_maths_set1.pdf',
    'f:/exam/backend/uploads/papers/cbse-10/cbse_2015_maths_set1.pdf',
]

for f in files_to_check:
    print(f"{f}: {'EXISTS' if os.path.exists(f) else 'MISSING!'}")
