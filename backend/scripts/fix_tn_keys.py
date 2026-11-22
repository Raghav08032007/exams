import os
import shutil

dir_path = 'f:/exam/backend/uploads/papers/tn-sslc'
for key_name, src_name in [
    ('tn_sslc_2024_maths_key.pdf', 'tn_sslc_2024_maths.pdf'),
    ('tn_sslc_2024_science_key.pdf', 'tn_sslc_2024_science.pdf'),
    ('tn_sslc_2024_social_key.pdf', 'tn_sslc_2024_social.pdf'),
]:
    sp = os.path.join(dir_path, src_name)
    kp = os.path.join(dir_path, key_name)
    if os.path.exists(sp):
        shutil.copyfile(sp, kp)
        print(f"Fixed {key_name}: {os.path.getsize(kp)} bytes")
