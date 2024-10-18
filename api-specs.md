
# register

## 화면 구성
1. input
    - username
        - type: text
    - password1
        - type: password
    - password2
        - type: password

2. button
- 등록
    - type: submit

## client validation
- 입력 유무:
    - `username`, `password1`, `password2` 모두 입력 유무
- 암호 유효성: 
    - `password1`과 `password2`가 동일한지 체크
    - `password`의 길이, 조합이 유효한지 체크

## api validation
- 등록 유무: 
    - `username`으로 이미 등록된 유저인지 체크
- 입력 유무:
    - `username`, `password1`, `password2` 모두 입력 유무
- 암호 유효성: 
    - `password1`과 `password2`가 동일한지 체크
    - `password`의 길이, 조합이 유효한지 체크

## API Interface
1. request
    - method: POST
    - endpoint: `api/v1/users/`
    - body:
        - username
        - password1
        - password2
2. response
    - format:
        - status: HttpStatus
        - messages: message array

        ```json
        {
            "status": 400,
            "messages": ["message1"]
        }
        ```
    1. error
        1. 이미 등록된 유저
            - status: 409 Conflict
        2. validation failed
            - status: 400 BAD_REQUEST
            - messages:
                - type: array
        3. 기타 4XX
        4. 기타 5XX
    2. success
        - status: 201
        - message: 없음
    