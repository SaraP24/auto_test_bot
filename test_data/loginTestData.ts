import { ILoginCredentials } from '../interfaces/ui/ILoginCredentials';

const loginTestData: {
    valid: ILoginCredentials[];
    invalid: ILoginCredentials[];
} = {
    valid: [
        {
            username: 'user1@example.com',
            password: 'ValidPassword123'
        },
        {
            username: 'user2@example.com',
            password: 'AnotherValidPass456'
        }
    ],
    invalid: [
        {
            username: '',
            password: ''
        },
        {
            username: 'user1@example.com',
            password: 'wrongpassword'
        }
    ]
};

export default loginTestData;