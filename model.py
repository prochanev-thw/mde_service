from pydantic import BaseModel, Field
import typing as t


class VideoNote(BaseModel):
    duration: int
    file_id: str
    file_unique_id: str


class From(BaseModel):
    first_name: str
    last_name: str
    id: int
    username: str


class Message(BaseModel):
    message_id: int
    message_date: int = Field(..., alias='date')
    from_user: From = Field(..., alias='from')
    text: t.Optional[str] = None
    video_note: t.Optional[VideoNote] = None


class Update(BaseModel):
    message: Message
    update_id: int

    def to_tuple(self):
        return (
            self.message.message_date,
            self.message.from_user.id,
            self.message.text,
            self.message.video_note.duration if self.message.video_note else None,
            self.message.video_note.file_unique_id  if self.message.video_note else None,
        )
