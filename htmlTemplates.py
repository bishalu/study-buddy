css = '''
<style>
.chat-message {
    padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex
}
.chat-message.user {
    background-color: #2b313e
}
.chat-message.bot {
    background-color: #475063
}
.chat-message .avatar {
  width: 20%;
}
.chat-message .avatar img {
  max-width: 78px;
  max-height: 78px;
  border-radius: 50%;
  object-fit: cover;
}
.chat-message .message {
  width: 80%;
  padding: 0 1.5rem;
  color: #fff;
}

input[type=radio]:checked+div {
    font-weight: bold;
    color:white;
}
.st-bn{
    margin: 0 auto;
    width: 80%;
    background-color: #303b4a;
    margin-top: 10px;
    padding: 10px;

}
.st-ce{
    width:100%;
    padding:10px 0px 10px 20px;
    border-radius:2px;
    color:#8592A5;
}
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://w7.pngwing.com/pngs/826/876/png-transparent-chimpanzee-logo-monkey-ape-monkey-face-animals-head-thumbnail.png" style="max-height: 78px; max-width: 78px; border-radius: 50%; object-fit: cover;">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="https://thumbs.dreamstime.com/b/male-student-graduation-avatar-profile-over-white-background-vector-illustration-81931258.jpg">
    </div>    
    <div class="message">{{MSG}}</div>
</div>
'''
