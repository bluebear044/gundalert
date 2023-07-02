import logging

# 로거 생성
logger = logging.getLogger('gund_logger')
logger.setLevel(logging.DEBUG)

# 로그 파일 경로 설정
log_file_path = 'gundalert.log'

# 로그 핸들러 생성 (파일 핸들러)
file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
file_handler.setLevel(logging.INFO)

# 로그 포맷 설정
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)

# 로그 핸들러 추가
logger.addHandler(file_handler)
