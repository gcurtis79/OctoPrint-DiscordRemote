from future.backports import datetime

COLOR_SUCCESS = 0x00AE86
COLOR_ERROR = 0xE84A4A
COLOR_INFO = 0xF2E82B

MAX_TITLE = 256
MAX_VALUE = 1024
MAX_DESCRIPTION = 2048
MAX_EMBED_LENGTH = 6000
MAX_NUM_FIELDS = 25


def embed_simple(title=None, description=None, color=None, snapshot=None):
    builder = EmbedBuilder()
    if color:
        builder.set_color(color)
    if title:
        builder.set_title(title)
    if description:
        builder.set_description(description)
    if snapshot:
        builder.set_snapshot(snapshot)
    return builder.get_embeds()


def success_embed(title=None, description=None):
    return embed_simple(title, description, COLOR_SUCCESS)


def error_embed(title=None, description=None):
    return embed_simple(title, description, COLOR_ERROR)


def info_embed(title=None, description=None):
    return embed_simple(title, description, COLOR_INFO)


class EmbedBuilder:
    def __init__(self):
        self.color = COLOR_INFO
        self.embeds = [Embed()]
        self.timestamp = True

    def set_color(self, color):
        self.color = color
        return self

    def set_title(self, title):
        if title is None:
            title = ""
        elif len(title) > MAX_TITLE:
            title = title[0:MAX_TITLE-3] + "..."

        while not self.embeds[-1].set_title(title):
            self.embeds.append(Embed())

        return self

    def set_description(self, description):
        if description is None:
            description = ""
        elif len(description) > MAX_DESCRIPTION:
            description = description[0:MAX_DESCRIPTION-3] + "..."

        while not self.embeds[-1].set_description(description):
            self.embeds.append(Embed())

        return self

    def add_field(self, title, text, inline=False):
        if title and len(str(title)) > MAX_TITLE:
            title = title[0:MAX_TITLE-3] + "..."
        if text and len(str(text)) > MAX_VALUE:
            text = text[0:MAX_VALUE - 3] + "..."

        while not self.embeds[-1].add_field({'name': str(title), 'value': str(text), 'inline': inline}):
            self.embeds.append(Embed())

        return self

    def enable_timestamp(self, enable):
        self.timestamp = enable
        return self

    # def set_image(self, snapshot):
    #     self.embeds[-1].set_image(snapshot)
    #     return self

    def get_embeds(self):
        # Finalise changes to embeds
        self.embeds[-1].timestamp = self.timestamp

        finalised = []
        for embed in self.embeds:
            embed.color = self.color

            finalised.append(embed.get_embed())

        return finalised


class Embed:
    def __init__(self):
        self.embed_length = 0
        self.color = COLOR_INFO
        self.title = None
        self.description = None
        self.timestamp = True
        self.fields = []
        self.image = None
        self.files = []

    def set_title(self, title):
        current_length = 0
        if self.title:
            current_length = len(self.title)
        if self.embed_length - current_length + len(title) > MAX_EMBED_LENGTH:
            return False
        self.embed_length -= current_length
        self.title = title
        self.embed_length += len(self.title)
        return True

    def set_description(self, description):
        current_length = 0
        if self.description:
            current_length = len(self.description)
        if self.embed_length - current_length + len(description) > MAX_EMBED_LENGTH:
            return False
        self.embed_length -= current_length
        self.description = description
        self.embed_length += len(self.description)
        return True

    def add_field(self, field):
        if len(self.fields) == MAX_NUM_FIELDS:
            return False

        field_length = 0
        if 'name' in field and field['name']:
            field_length += len(field['name'])
        if 'value' in field and field['value']:
            field_length += len(field['value'])

        if self.embed_length + field_length > MAX_EMBED_LENGTH:
            return False

        self.fields.append(field)
        self.embed_length += field_length
        return True

    def set_image(self, snapshot):
        self.image = {'url': "attachment://%s" % snapshot[0]}
        self.files.append(snapshot)
        pass

    def get_embed(self):
        embed = {'fields': self.fields}
        if self.title:
            embed['title'] = self.title
        if self.description:
            embed['description'] = self.description
        if self.timestamp:
            embed['timestamp'] = datetime.datetime.utcnow().isoformat()
        if self.color:
            embed['color'] = self.color
        if self.image:
            embed['image'] = self.image
        return embed

    def get_files(self):
        return self.files
