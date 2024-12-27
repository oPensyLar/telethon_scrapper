from telethon.tl.functions.channels import GetParticipantsRequest, GetFullChannelRequest
from telethon.errors.rpcerrorlist import (FloodWaitError, ChatAdminRequiredError)
from telethon.tl.types import InputPeerChat
from telethon.tl.types import (ChannelParticipantsSearch, ChatForbidden, InputPeerEmpty, Chat, Channel)
from telethon.tl.functions.messages import (GetDialogsRequest, GetHistoryRequest, GetRepliesRequest, GetFullChatRequest)
from telethon.tl.types import (InputPeerEmpty, InputChannel)
from telethon.sync import TelegramClient, events
from telethon.errors.rpcerrorlist import PeerIdInvalidError
import time

class TgScrap:
    def __init__(self, file_name, api_id, api_hash):
        self.channel_full_info = None
        self.chats = []
        self.app_id = api_id
        self.app_hash = api_hash
        self.token_file_path = file_name
        self.client = None
        self.phone_number = None
        self.me = None

    def set_phone_number(self, phone):
        self.phone_number = phone

    def close(self):
        self.client.disconnect()

    def get_dialogs(self, listen_chat=None):
        if listen_chat is None:
            return {"client": self.client, "dialogs": self.client.iter_dialogs()}
        else:
            for dialog in self.client.iter_dialogs():
                if dialog.id == listen_chat:
                    return {"client": self.client, "dialog": dialog}

    def connect(self):
        ret = {"code": 0x0}
        try:
            self.client = TelegramClient(self.token_file_path, self.app_id, self.app_hash)
            self.client.connect()

        except ConnectionError:
            ret['code'] = -1
            return ret

        if not self.client.is_user_authorized():
            self.client.send_code_request(self.phone_number)
            self.me = self.client.sign_in(self.phone_number, input('Enter code: '))

        ret['code'] = 0x0
        return ret

    def enum_members(self, group_obj):
        for chat in self.chats:
            members = self.client.get_participants(chat, aggressive=True)
            print(members)

    def test_members_1(self, channel_data, folder_name, cb_users, last_checkpoint):

        # is ChatForbidden
        if isinstance(channel_data, ChatForbidden):
            return

        if isinstance(channel_data, Chat):
            return

        if isinstance(channel_data, Channel):
            return

        query_key = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
        offset = None
        cb_data = None
        all_participants = []

        if last_checkpoint is not None:
            filtred_chars = []
            index = 0x0
            add = False

            for one_key in query_key:
                if ord(one_key) >= ord(last_checkpoint["letra"]):
                    filtred_chars.append(one_key)

            offset = last_checkpoint["offset"]
            query_key = filtred_chars

        else:
            query_key = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
            offset = 0

        for key in query_key:
            limit = 2300

            while True:
                try:
                    cb_data = self.client(GetParticipantsRequest(channel_data.username, ChannelParticipantsSearch(key), offset, limit, hash=0))

                except ChatAdminRequiredError:
                    return None

                except (ConnectionError, TypeError):
                    print("[!] ConnectionError or TypeError on test_members_1() SLEPING..!")
                    time.sleep(5)
                    continue

                if not cb_data.users:
                    break

                cb_users(channel_data, cb_data, folder_name, key, offset)
                offset += len(cb_data.users)

    def test_members(self, channel_str, fracciones_members):
        offset = 0x0
        limit = 0x0
        all_particioants = []

        while True:
            channel_entity = self.client.get_entity(channel_str)

            self.channel_full_info = self.client(
                GetFullChannelRequest(channel=channel_entity))

            total_offset = self.channel_full_info.full_chat.participants_count / fracciones_members
            total_offset = int(total_offset)+0x1

            while offset is not total_offset:
                participants = self.client(GetParticipantsRequest(
                    channel_entity,
                    ChannelParticipantsSearch(''),
                    offset,
                    fracciones_members,
                    hash=0))

                offset += 0x1

                all_particioants.append(participants)

            participants = self.client(GetParticipantsRequest(
                channel_str, ChannelParticipantsSearch(''),
                offset,
                limit,
                hash=0))

    def get_chats(self):
        return self.chats

    def send_message(self, entity, text, msg_id=False):
        peer_chat = self.client.get_entity(entity)
        self.client.send_message(entity=peer_chat, message=text, reply_to=msg_id)

    def get_messages(self, chat_id, limit=None, fech=None):
        msg_lst = []
        for message in self.client.iter_messages(chat_id, limit=limit, offset_date=fech):
            # print(message.sender_id, ':', message.text)
            msg_lst.append(message)

        return msg_lst

    def get_historical(self, entity, start_from, limit_msg):
        try:
            posts = self.client(GetHistoryRequest(
                peer=entity,
                limit=limit_msg,
                offset_date=start_from,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0))
        except FloodWaitError:
            return None

        return posts

    def get_members(self, group):
        try:
            users = self.client.get_participants(group)

        except (PeerIdInvalidError, TypeError, ConnectionError, ChatAdminRequiredError):
            return None            

        lista_users = []
        i = 0x0

        for user in users:
            i += 0x1
            json_obj = {str(i): {"username": user.username,
                                 "first_name": user.first_name,
                                 "second_name": user.last_name,
                                 "phone": user.phone,
                                 "id": user.id,
                                 "group_id": group.id,
                                 "group_name": group.title}}

            lista_users.append(json_obj)

        return lista_users

    def enum_groups(self):
        ret_data = self.client(GetDialogsRequest(offset_date=None, offset_id=0, offset_peer=InputPeerEmpty(), limit=200, hash=0))
        self.chats = []
        self.chats.extend(ret_data.chats)

