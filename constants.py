# Определяем параметры и их зависимости
param_types = ['face', 'hair_length', 'hair_type', 'hair_color']

next_param = {
    'face': 'hair_length',
    'hair_length': 'hair_type',
    'hair_type': 'hair_color',
    'hair_color': None
}
step_data = {
    'face': {'image': 'assets/1.jpg', 'caption': 'Выберите форму лица:'},
    'hair_length': {'image': 'assets/2.jpg', 'caption': 'Выберите длину волос:'},
    'hair_type': {'image': 'assets/3.jpg', 'caption': 'Выберите тип волос:'},
    'hair_color': {'image': 'assets/4.jpg', 'caption': 'Выберите цвет волос:'}
}
param_dependencies = {
    'face': [],
    'hair_length': ['face'],
    'hair_type': ['face', 'hair_length'],
    'hair_color': ['face', 'hair_length', 'hair_type']
}