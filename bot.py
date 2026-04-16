import os
import re
import json
import datetime
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple

import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# =========================================================
#  TOKEN (.env)
# =========================================================
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# =========================================================
#  IDS / CONFIG SUPREMO
# =========================================================

# Categorias de ticket de RECRUTAMENTO (tenta a primeira válida)
TICKETS_CATEGORY_IDS: List[int] = [
    1400279269724127252,
    1400864188020162731,
    1420262084792422470,
    1466214565447598163,
]

CANAL_TELEFONE_ID = 1385888659869274124
CANAL_RECRUTADOS_ID = 1468399773039067399

# Logs gerais
CANAL_TICKETS_ABERTOS_ID = 1468400008947695829
CANAL_TICKETS_FECHADOS_ID = 1468400030095249460

# Recrutamento: quem pode aprovar/reprovar (recrutador OU admin)
CARGO_RECRUTADOR_ID = 1386446336479723561

# Cargos ao aprovar recrutamento
CARGO_SUPREMO_ID = 1386445230986760262
CARGO_OLHEIRO_ID = 1386446066127212634

# Canal hierarquia (painel e logs)
HIERARQUIA_CANAL_ID = 1385876581075124305

# =========================================================
#  HIERARQUIA (ORDEM EXATA)
#  00 primeiro ... OLHEIRO por último
# =========================================================
HIERARQUIA_ROLE_IDS_ORDERED: List[int] = [
    1384004284282179719,  # 🏅00
    1386447068889092176,  # 🏅01
    1386447351710875850,  # 🏅02
    1386440971620978932,  # 🏅03
    1386441395165986908,  # SUB.LIDER
    1386441647792984188,  # RESP. GERAL
    1386441919239819355,  # RESP. FARM
    1386442183686750279,  # RESP. REC
    1386442008683614379,  # RESP. ELITE
    1386443545141051543,  # RESP. AÇÃO
    1386443388177350696,  # RESP. PAG
    1386442668535713812,  # RESP. CONTAB.
    1386442762139734197,  # RESP. COMERCIAL
    1386443201866498129,  # RESP. ORGANIZAÇÃO
    1386443750670209184,  # RESP. FESTA
    1386444521419575466,  # GRT. FARM
    1386444326896144505,  # GRT. REC
    1386444687941832778,  # GRT. VENDA
    1386446336479723561,  # RECRUTADOR
    1386444927847628840,  # ELITE
    1386445522444750929,  # MEMBRO
    1386446066127212634,  # OLHEIRO
]
HIERARQUIA_ROLE_IDS = HIERARQUIA_ROLE_IDS_ORDERED[:]

# =========================================================
#  SUPORTE (AJUDA)
# =========================================================
CATEGORIA_TICKETS_AJUDA_ID = 1386251868140863510
CANAL_PAINEL_AJUDA_ID = 1386252604312522892

# =========================================================
#  ADV
# =========================================================
CANAL_PAINEL_ADV_ID = 1393348811950129203
CANAL_LOG_ADV_ID = 1386254146184679476
ADV_LEVE_ID = 1388987481558351973
ADV_MODERADA_ID = 1393350074867777677
ADV_GRAVE_ID = 1393351074739392543

# =========================================================
#  PEDIR TAG (painel)
# =========================================================
CANAL_PAINEL_PEDIR_TAG_ID = 1471235682436386997
CATEGORIA_TICKET_TESTE_ELITE_ID = 1386531885315919953

# =========================================================
#  PEDIDOS / ENCOMENDAS
# =========================================================
CANAL_PEDIDOS_ID = 1468400514306674740
CANAL_ENCOMENDAS_ID = 1468400467015893065

# =========================================================
#  CORES
# =========================================================
COR_PENDENTE = 0x2F3136
COR_APROVADO_MARROM = 0x8B5A2B
COR_REPROVADO_VERMELHO = 0xFF0000
COR_INFO = 0x5865F2

# =========================================================
#  METAS / RESUMO
# =========================================================
RESUMO_META_TEXTO = (
    "📋📋📋 **RESUMO DE ENTREGAS / METAS – SUPREMO** 📋📋📋\n\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n"
    "🔹 **OLHEIRO**\n"
    "📦 Entrega: **120 PRATAS** **OU** **200 CANOS / MOLAS / GATILHOS**\n"
    "💰 Recompensa: **250K + 1 PT + 50 MUNIÇÕES**\n"
    "📈 Quanto mais entrega, **MAIOR A RECOMPENSA**.\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "🔹 **MEMBRO**\n"
    "📦 Entrega semanal:\n"
    "• **100 PRATAS**\n"
    "• **100 GATILHOS**\n"
    "• **200 CANOS**\n"
    "• **200 MOLAS**\n"
    "💰 Recompensa: **600K POR ENTREGA COMPLETA**\n"
    "📈 Quanto mais entrega, **MAIOR A RECOMPENSA**.\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "🔹 **ELITE**\n"
    "🎯 Meta: **NO MÍNIMO 3 PT DE PISTA / AÇÃO A CADA 2 DIAS**\n"
    "💰 Recompensa semanal: **300K A 600K (CONFORME DESEMPENHO)**\n"
    "📈 Quanto mais desempenho, **MAIOR A RECOMPENSA**.\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "🔹 **RECRUTADOR**\n"
    "👥 Recrutar **NO MÍNIMO 5 NOVOS MEMBROS POR SEMANA**\n"
    "💰 Recompensa: **250K POR PESSOA RECRUTADA**\n"
    "📈 Quanto mais recruta, **MAIOR A RECOMPENSA**.\n"
    "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    "⚠️⚠️⚠️ **ATENÇÃO** ⚠️⚠️⚠️\n"
    "✅ **TODAS AS INFORMAÇÕES DEVEM SER REGISTRADAS CORRETAMENTE NO TICKET**\n"
    "✅ **SEM REGISTRO = SEM PAGAMENTO**\n"
)

# =========================================================
#  BOT / INTENTS
# =========================================================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # necessário pro !setmeuticket
bot = commands.Bot(command_prefix="!", intents=intents)

# =========================================================
#  PERSISTÊNCIA (JSON)
# =========================================================
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

SET_TICKET_FILE = os.path.join(DATA_DIR, "meu_ticket_map.json")
HIERARQUIA_PANEL_FILE = os.path.join(DATA_DIR, "hierarquia_panel.json")

def load_json(path: str, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path: str, obj):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[JSON] Erro ao salvar {path}: {e}")

MEU_TICKET_MAP: Dict[str, int] = load_json(SET_TICKET_FILE, {})
HIERARQUIA_PANEL = load_json(HIERARQUIA_PANEL_FILE, {"channel_id": None, "message_id": None})

# =========================================================
#  RECRUTAMENTO: MEMÓRIA
# =========================================================
@dataclass
class RecruitData:
    member_id: int
    nome_personagem: str
    id_personagem: str
    telefone: str
    id_recrutador: str
    status: str = "PENDENTE"
    embed_message_id: int = 0
    action_message_id: int = 0

recruits_by_ticket: Dict[int, RecruitData] = {}

# =========================================================
#  HELPERS GERAIS
# =========================================================
def sanitize_name(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9\-]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value[:40] if value else "ticket"

def is_recrutador(member: discord.Member) -> bool:
    if member.guild_permissions.administrator:
        return True
    return any(r.id == CARGO_RECRUTADOR_ID for r in member.roles)

def is_admin(member: discord.Member) -> bool:
    return member.guild_permissions.administrator

def pick_recruit_category(guild: discord.Guild) -> Optional[discord.CategoryChannel]:
    for cid in TICKETS_CATEGORY_IDS:
        ch = guild.get_channel(cid)
        if isinstance(ch, discord.CategoryChannel):
            return ch
    return None

async def send_logo_embed_message(dest: discord.abc.Messageable, embed: discord.Embed) -> discord.Message:
    file = discord.File("logo.png", filename="logo.png")
    embed.set_thumbnail(url="attachment://logo.png")
    return await dest.send(embed=embed, file=file)

async def log_ticket_aberto(guild: discord.Guild, texto: str):
    ch = guild.get_channel(CANAL_TICKETS_ABERTOS_ID)
    if isinstance(ch, discord.TextChannel):
        await ch.send(texto)

async def log_ticket_fechado(guild: discord.Guild, texto: str, file: Optional[discord.File] = None):
    ch = guild.get_channel(CANAL_TICKETS_FECHADOS_ID)
    if isinstance(ch, discord.TextChannel):
        if file:
            await ch.send(texto, file=file)
        else:
            await ch.send(texto)

def get_hierarquia_roles(guild: discord.Guild) -> List[discord.Role]:
    roles = []
    for rid in HIERARQUIA_ROLE_IDS:
        r = guild.get_role(rid)
        if r:
            roles.append(r)
    return roles

async def set_hierarquia_role(member: discord.Member, new_role_id: int, reason: str = "Mudança de hierarquia"):
    guild = member.guild
    hier_roles = get_hierarquia_roles(guild)
    new_role = guild.get_role(new_role_id)
    if not new_role:
        return
    to_remove = [r for r in hier_roles if r in member.roles and r.id != new_role_id]
    if to_remove:
        await member.remove_roles(*to_remove, reason=reason)
    if new_role not in member.roles:
        await member.add_roles(new_role, reason=reason)

# =========================================================
#  TRANSCRIPT TXT (NORMAL)
# =========================================================
async def build_text_transcript(channel: discord.TextChannel) -> Tuple[str, str]:
    lines = []
    async for msg in channel.history(limit=None, oldest_first=True):
        ts = msg.created_at.strftime("%d/%m/%Y %H:%M")
        author = getattr(msg.author, "display_name", "Unknown")
        content = msg.content or ""
        att = ""
        if msg.attachments:
            att = " | ANEXOS: " + " ".join(a.url for a in msg.attachments)
        emb = ""
        if msg.embeds:
            e = msg.embeds[0]
            t = (e.title or "").strip()
            d = (e.description or "").strip()
            if t or d:
                emb = f" | EMBED: {t} - {d[:300]}"
        lines.append(f"[{ts}] {author}: {content}{att}{emb}")

    text = "\n".join(lines) if lines else "(sem mensagens)"
    filepath = os.path.join(DATA_DIR, f"transcript-{channel.id}.txt")
    filename = f"transcript-{channel.name}.txt"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(text)
    return filepath, filename

# =========================================================
#  HIERARQUIA AO VIVO (CORRIGIDO)
# =========================================================
def member_display_line(m: discord.Member) -> str:
    nick = m.display_name
    return f"{m.mention} ({nick})"

def chunk_text_lines(lines: List[str], max_len: int = 1000) -> List[str]:
    chunks = []
    current = ""

    for line in lines:
        add = line if not current else f"\n{line}"
        if len(current) + len(add) <= max_len:
            current += add
        else:
            if current:
                chunks.append(current)
            current = line[:max_len]

    if current:
        chunks.append(current)

    return chunks if chunks else ["*(vazio)*"]

def build_hierarquia_embeds(guild: discord.Guild) -> List[discord.Embed]:
    embeds: List[discord.Embed] = []
    page = 1
    total_membros = 0

    current_embed = discord.Embed(
        title=f"🏆 HIERARQUIA SUPREMO • Página {page}",
        description="📌 Painel automático da hierarquia atual.",
        color=COR_INFO
    )

    current_chars = len(current_embed.title or "") + len(current_embed.description or "")
    current_fields = 0

    for rid in HIERARQUIA_ROLE_IDS_ORDERED:
        role = guild.get_role(rid)
        if not role:
            continue

        members = [m for m in role.members if not m.bot]
        members.sort(key=lambda x: (x.display_name or "").lower())
        total_membros += len(members)

        if members:
            member_lines = [member_display_line(m) for m in members]
            value_chunks = chunk_text_lines(member_lines, max_len=1000)
        else:
            value_chunks = ["*(vazio)*"]

        for idx, chunk in enumerate(value_chunks):
            field_name = f"{role.name} [{len(members)}]"
            if idx > 0:
                field_name = f"{role.name} [continuação]"

            field_cost = len(field_name) + len(chunk)

            if current_fields >= 25 or (current_chars + field_cost) > 5800:
                embeds.append(current_embed)
                page += 1
                current_embed = discord.Embed(
                    title=f"🏆 HIERARQUIA SUPREMO • Página {page}",
                    description="📌 Continuação do painel automático.",
                    color=COR_INFO
                )
                current_chars = len(current_embed.title or "") + len(current_embed.description or "")
                current_fields = 0

            current_embed.add_field(name=field_name, value=chunk, inline=False)
            current_fields += 1
            current_chars += field_cost

    if current_fields == 0:
        current_embed.add_field(name="Hierarquia", value="Sem dados.", inline=False)

    current_embed.set_footer(text=f"Total listado: {total_membros} membro(s)")
    embeds.append(current_embed)

    # garante footer na última página
    if embeds:
        embeds[-1].set_footer(text=f"Total listado: {total_membros} membro(s)")

    return embeds[:10]  # Discord aceita até 10 embeds por mensagem

async def ensure_hierarquia_panel(guild: discord.Guild) -> Optional[discord.Message]:
    ch = guild.get_channel(HIERARQUIA_CANAL_ID)
    if not isinstance(ch, discord.TextChannel):
        print("[HIERARQUIA] Canal inválido.")
        return None

    msg = None
    if HIERARQUIA_PANEL.get("channel_id") and HIERARQUIA_PANEL.get("message_id"):
        try:
            if int(HIERARQUIA_PANEL["channel_id"]) == ch.id:
                msg = await ch.fetch_message(int(HIERARQUIA_PANEL["message_id"]))
        except Exception as e:
            print(f"[HIERARQUIA] Não consegui buscar painel salvo: {e}")
            msg = None

    if msg is None:
        embed = discord.Embed(
            title="🏆 HIERARQUIA SUPREMO",
            description="📌 Painel automático — atualiza quando aprova recrutamento / aprova pedir tag / teste elite.",
            color=COR_INFO
        )
        try:
            msg = await send_logo_embed_message(ch, embed)
            HIERARQUIA_PANEL["channel_id"] = ch.id
            HIERARQUIA_PANEL["message_id"] = msg.id
            save_json(HIERARQUIA_PANEL_FILE, HIERARQUIA_PANEL)
            print(f"[HIERARQUIA] Novo painel criado. Message ID: {msg.id}")
        except Exception as e:
            print(f"[HIERARQUIA] Erro ao criar painel: {e}")
            return None

    return msg

async def update_hierarquia_panel(guild: discord.Guild):
    msg = await ensure_hierarquia_panel(guild)
    if msg is None:
        print("[HIERARQUIA] Não foi possível garantir painel.")
        return

    try:
        embeds = build_hierarquia_embeds(guild)
        if not embeds:
            embeds = [
                discord.Embed(
                    title="🏆 HIERARQUIA SUPREMO",
                    description="Sem dados.",
                    color=COR_INFO
                )
            ]

        file = discord.File("logo.png", filename="logo.png")
        embeds[0].set_thumbnail(url="attachment://logo.png")

        await msg.edit(embeds=embeds, attachments=[file])
        print("[HIERARQUIA] Painel atualizado com sucesso.")
    except Exception as e:
        print(f"[HIERARQUIA] Erro ao editar painel: {e}")

# =========================================================
#  MONEY / PARSERS
# =========================================================
def parse_int(v: str) -> int:
    v = (v or "").strip()
    if not v:
        return 0
    v = re.sub(r"[^\d]", "", v)
    return int(v) if v else 0

def fmt_money_k(n: int) -> str:
    # 1000 = 1k, 1.000.000 = 1kk
    if n >= 1_000_000:
        return f"{n/1_000_000:.3f}kk".replace(".", ",")
    if n >= 1_000:
        return f"{n/1_000:.1f}k".replace(".", ",")
    return str(n)

def normalize_item_name(s: str) -> str:
    s = s.strip().lower()
    s = s.replace("á","a").replace("à","a").replace("ã","a").replace("â","a")
    s = s.replace("é","e").replace("ê","e")
    s = s.replace("í","i")
    s = s.replace("ó","o").replace("ô","o").replace("õ","o")
    s = s.replace("ú","u")
    return s

def parse_lines_item_qty(text: str, normalize_names: bool = True) -> List[Tuple[str, int]]:
    """
    Aceita linhas:
    celular=500
    mochila 200
    C4:10
    """
    items = []
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        if "=" in line:
            a, b = line.split("=", 1)
        elif ":" in line:
            a, b = line.split(":", 1)
        else:
            parts = line.split()
            if len(parts) < 2:
                continue
            a, b = " ".join(parts[:-1]), parts[-1]

        name = a.strip()
        if normalize_names:
            name = normalize_item_name(name)

        qty = parse_int(b)
        if qty > 0:
            items.append((name, qty))
    return items

# =========================================================
#  RECRUTAMENTO: EMBED/STATUS
# =========================================================
def build_recruit_embed(data: RecruitData, member_mention: str, status_text: str, color: int, footer: str = "") -> discord.Embed:
    desc = (
        f"👤 **Recrutado:** {member_mention}\n"
        f"🎭 **Nome do personagem:** `{data.nome_personagem}`\n"
        f"🆔 **ID:** `{data.id_personagem}`\n"
        f"📞 **Telefone:** `{data.telefone}`\n"
        f"🧑‍💼 **ID do Recrutador:** `{data.id_recrutador}`\n\n"
        f"{status_text}"
    )
    embed = discord.Embed(title="📋 RECRUTAMENTO - SUPREMO", description=desc, color=color)
    if footer:
        embed.set_footer(text=footer)
    return embed

async def remove_buttons_by_message(channel: discord.TextChannel, message_id: int):
    try:
        msg = await channel.fetch_message(message_id)
        await msg.edit(view=None)
    except Exception as e:
        print(f"[RECRUTAMENTO] Erro ao remover botões: {e}")

async def update_recruit_embed(channel: discord.TextChannel, data: RecruitData, status_text: str, color: int, footer: str):
    if not data.embed_message_id:
        return
    try:
        msg = await channel.fetch_message(data.embed_message_id)
        embed = build_recruit_embed(
            data=data,
            member_mention=f"<@{data.member_id}>",
            status_text=status_text,
            color=color,
            footer=footer
        )
        file = discord.File("logo.png", filename="logo.png")
        embed.set_thumbnail(url="attachment://logo.png")
        await msg.edit(embed=embed, attachments=[file])
    except Exception as e:
        print(f"[RECRUTAMENTO] Erro ao atualizar embed: {e}")

# =========================================================
#  MODAL RECRUTAMENTO
# =========================================================
class RecruitModal(discord.ui.Modal, title="FORMULÁRIO DE RECRUTAMENTO - SUPREMO"):
    nome_personagem = discord.ui.TextInput(label="Nome do Personagem", placeholder="Ex: Alberto", max_length=32)
    id_personagem = discord.ui.TextInput(label="ID do Personagem", placeholder="Ex: 1234", max_length=16)
    telefone = discord.ui.TextInput(label="Telefone In-Game", placeholder="Ex: 710-271", max_length=32)
    id_recrutador = discord.ui.TextInput(label="ID do Recrutador", placeholder="Ex: 244507", max_length=24)

    async def on_submit(self, interaction: discord.Interaction):
        if interaction.guild is None or not isinstance(interaction.user, discord.Member):
            return await interaction.response.send_message("❌ Use isso dentro do servidor.", ephemeral=True)

        guild = interaction.guild
        member = interaction.user

        category = pick_recruit_category(guild)
        if category is None:
            return await interaction.response.send_message("❌ Nenhuma categoria de recrutamento válida encontrada.", ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        }

        recrut_role = guild.get_role(CARGO_RECRUTADOR_ID)
        if recrut_role:
            overwrites[recrut_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        nome = str(self.nome_personagem.value).strip()
        pid = str(self.id_personagem.value).strip()

        channel_name = f"{sanitize_name(nome)}-{pid}"[:95]
        channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            reason="Ticket recrutamento SUPREMO",
        )

        data = RecruitData(
            member_id=member.id,
            nome_personagem=nome,
            id_personagem=pid,
            telefone=str(self.telefone.value).strip(),
            id_recrutador=str(self.id_recrutador.value).strip(),
        )
        recruits_by_ticket[channel.id] = data

        embed = build_recruit_embed(
            data=data,
            member_mention=member.mention,
            status_text="⏳ **STATUS: PENDENTE**",
            color=COR_PENDENTE,
            footer="Aguardando aprovação."
        )
        embed_msg = await send_logo_embed_message(channel, embed)
        data.embed_message_id = embed_msg.id

        action_msg = await channel.send("✅ Recrutador/Staff: use os botões abaixo:", view=ApproveView())
        data.action_message_id = action_msg.id

        await log_ticket_aberto(
            guild,
            f"🟢 **TICKET ABERTO (RECRUTAMENTO)** | Autor: {member.mention} (`{member.id}`) | Canal: {channel.mention}"
        )

        await interaction.response.send_message(f"✅ Ticket criado: {channel.mention}", ephemeral=True)

# =========================================================
#  VIEWS RECRUTAMENTO
# =========================================================
class StartRecruitView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📋 PREENCHER RECRUTAMENTO", style=discord.ButtonStyle.success, custom_id="supremo:start_recruit")
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RecruitModal())

class ApproveView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✅ APROVAR", style=discord.ButtonStyle.success, custom_id="supremo:approve")
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        if interaction.guild is None or not isinstance(interaction.user, discord.Member):
            return await interaction.followup.send("❌ Isso só funciona no servidor.", ephemeral=True)

        if not is_recrutador(interaction.user):
            return await interaction.followup.send("⛔ Você não tem permissão para aprovar.", ephemeral=True)

        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            return await interaction.followup.send("❌ Canal inválido.", ephemeral=True)

        data = recruits_by_ticket.get(channel.id)
        if not data:
            return await interaction.followup.send("❌ Não achei os dados desse ticket (bot reiniciou?).", ephemeral=True)

        if data.status != "PENDENTE":
            return await interaction.followup.send(f"⚠️ Já está `{data.status}`.", ephemeral=True)

        guild = channel.guild
        recruited = guild.get_member(data.member_id)

        await remove_buttons_by_message(channel, data.action_message_id)
        await update_recruit_embed(channel, data, "✅ **STATUS: APROVADO**", COR_APROVADO_MARROM, f"Aprovado por: {interaction.user.display_name}")

        role_supremo = guild.get_role(CARGO_SUPREMO_ID)
        role_olheiro = guild.get_role(CARGO_OLHEIRO_ID)

        if recruited:
            try:
                if role_supremo and role_supremo not in recruited.roles:
                    await recruited.add_roles(role_supremo, reason="Recrutamento aprovado (SUPREMO)")
                if role_olheiro and role_olheiro not in recruited.roles:
                    await recruited.add_roles(role_olheiro, reason="Recrutamento aprovado (OLHEIRO)")
            except discord.Forbidden:
                await channel.send("⚠️ Bot sem permissão pra mexer em cargos (Gerenciar Cargos).")

            try:
                await recruited.edit(nick=f"{data.nome_personagem} - {data.id_personagem}", reason="Recrutamento aprovado")
            except Exception:
                pass

        try:
            await channel.edit(name=f"{sanitize_name(data.nome_personagem)}-{data.id_personagem}"[:95], reason="Recrutamento aprovado")
        except Exception:
            pass

        data.status = "APROVADO"

        await channel.send("✅ **RECRUTAMENTO APROVADO!**")
        await channel.send(RESUMO_META_TEXTO)
        await channel.send(f"🟤 {interaction.user.mention} **VOCÊ RECRUTOU O MEMBRO `{data.id_personagem}`**")

        # manda também no "meu ticket" do aprovador (se ele setou)
        try:
            dest_id = MEU_TICKET_MAP.get(str(interaction.user.id))
            if dest_id:
                dest = guild.get_channel(int(dest_id))
                if isinstance(dest, discord.TextChannel):
                    await dest.send(
                        f"✅ **REGISTRO DE RECRUTAMENTO**\n"
                        f"Você recrutou/aprovou: `{data.nome_personagem} - {data.id_personagem}`\n"
                        f"Recrutado: <@{data.member_id}> | Ticket: {channel.mention}"
                    )
        except Exception:
            pass

        tel_ch = guild.get_channel(CANAL_TELEFONE_ID)
        if isinstance(tel_ch, discord.TextChannel):
            await tel_ch.send(f"📞 **NOVO TELEFONE** | `{data.telefone}` | `{data.nome_personagem}` | ID: `{data.id_personagem}`")

        log_ch = guild.get_channel(CANAL_RECRUTADOS_ID)
        if isinstance(log_ch, discord.TextChannel):
            await log_ch.send(
                f"✅ **RECRUTAMENTO APROVADO**\n"
                f"Recrutado: <@{data.member_id}> | Nome: `{data.nome_personagem}` | ID: `{data.id_personagem}`\n"
                f"Telefone: `{data.telefone}` | Recrutador (ID): `{data.id_recrutador}` | Aprovador: {interaction.user.mention}"
            )

        # Atualiza painel da HIERARQUIA
        await update_hierarquia_panel(guild)

        # 🔒 NOVO: se quem aprovou for RECRUTADOR (não-admin), perde acesso a ESTE ticket
        try:
            if isinstance(interaction.user, discord.Member) and not interaction.user.guild_permissions.administrator:
                await channel.set_permissions(
                    interaction.user,
                    overwrite=discord.PermissionOverwrite(view_channel=False),
                    reason="Após aprovar: recrutador não pode ver tickets de outros"
                )
        except Exception as e:
            print("Falha ao bloquear recrutador no ticket após aprovar:", e)

        await interaction.followup.send("✅ Aprovado! Status atualizado e botões removidos.", ephemeral=True)

    @discord.ui.button(label="❌ REPROVAR", style=discord.ButtonStyle.danger, custom_id="supremo:reject")
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        if interaction.guild is None or not isinstance(interaction.user, discord.Member):
            return await interaction.followup.send("❌ Isso só funciona no servidor.", ephemeral=True)

        if not is_recrutador(interaction.user):
            return await interaction.followup.send("⛔ Você não tem permissão para reprovar.", ephemeral=True)

        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            return await interaction.followup.send("❌ Canal inválido.", ephemeral=True)

        data = recruits_by_ticket.get(channel.id)
        if not data:
            return await interaction.followup.send("❌ Não achei os dados desse ticket (bot reiniciou?).", ephemeral=True)

        if data.status != "PENDENTE":
            return await interaction.followup.send(f"⚠️ Já está `{data.status}`.", ephemeral=True)

        guild = channel.guild

        await remove_buttons_by_message(channel, data.action_message_id)
        await update_recruit_embed(channel, data, "❌ **STATUS: REPROVADO**", COR_REPROVADO_VERMELHO, f"Reprovado por: {interaction.user.display_name}")

        data.status = "REPROVADO"
        await channel.send(f"❌ **RECRUTAMENTO REPROVADO** por {interaction.user.mention}.")

        await log_ticket_fechado(
            guild,
            f"🔴 **TICKET FECHADO (RECRUTAMENTO / REPROVADO)** | Autor: <@{data.member_id}> (`{data.member_id}`) | "
            f"Personagem: `{data.nome_personagem}` (`{data.id_personagem}`) | Reprovado por: {interaction.user.mention} | Canal: {channel.mention}"
        )

        # 🔒 NOVO: se quem reprovou for RECRUTADOR (não-admin), perde acesso a ESTE ticket
        try:
            if isinstance(interaction.user, discord.Member) and not interaction.user.guild_permissions.administrator:
                await channel.set_permissions(
                    interaction.user,
                    overwrite=discord.PermissionOverwrite(view_channel=False),
                    reason="Após reprovar: recrutador não pode ver tickets de outros"
                )
        except Exception as e:
            print("Falha ao bloquear recrutador no ticket após reprovar:", e)

        await interaction.followup.send("❌ Reprovado. Status atualizado e botões removidos.", ephemeral=True)

# =========================================================
#  SUPORTE (TICKETS)
# =========================================================
def help_ticket_overwrites(guild: discord.Guild, author: discord.Member) -> dict:
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(view_channel=False),
        author: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
    }
    for role in guild.roles:
        if role.permissions.administrator:
            overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
    return overwrites

async def create_help_ticket(guild: discord.Guild, author: discord.Member, kind: str, title: str, intro_text: str) -> Optional[discord.TextChannel]:
    category = guild.get_channel(CATEGORIA_TICKETS_AJUDA_ID)
    if not isinstance(category, discord.CategoryChannel):
        return None

    channel = await guild.create_text_channel(
        name=f"{kind}-{author.id}"[:95],
        category=category,
        overwrites=help_ticket_overwrites(guild, author),
        reason=f"Ticket suporte {kind} - {author}",
    )

    try:
        await channel.edit(topic=f"SUPREMO_HELP_TICKET|type={kind}|owner={author.id}")
    except Exception:
        pass

    embed = discord.Embed(title=title, description=intro_text, color=COR_PENDENTE)
    await send_logo_embed_message(channel, embed)

    await channel.send(f"{author.mention} ✅ Ticket criado! **Aguarde um administrador.**")
    await channel.send("🔧 **CONTROLES DO TICKET:**", view=TicketControlView())

    await log_ticket_aberto(
        guild,
        f"🟢 **TICKET ABERTO (SUPORTE)** | Tipo: **{kind.upper()}** | Autor: {author.mention} (`{author.id}`) | Canal: {channel.mention}"
    )
    return channel

class TicketControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🟡 ASSUMIR TICKET", style=discord.ButtonStyle.secondary, custom_id="supremo:ticket_assumir")
    async def assumir(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("⛔ Apenas administradores.", ephemeral=True)
        await interaction.response.send_message(f"🟡 Ticket assumido por: {interaction.user.mention}", ephemeral=False)

    @discord.ui.button(label="🔴 FECHAR TICKET", style=discord.ButtonStyle.danger, custom_id="supremo:ticket_fechar")
    async def fechar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            return await interaction.response.send_message("⛔ Apenas administradores.", ephemeral=True)

        await interaction.response.defer(ephemeral=True)

        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            return

        guild = channel.guild

        owner_id = None
        ticket_type = "desconhecido"
        try:
            if channel.topic and "SUPREMO_HELP_TICKET" in channel.topic:
                parts = dict(p.split("=", 1) for p in channel.topic.split("|")[1:] if "=" in p)
                ticket_type = parts.get("type", ticket_type)
                owner_id = int(parts.get("owner", "0")) or None
        except Exception:
            pass

        filepath, filename = await build_text_transcript(channel)

        if owner_id:
            try:
                member = guild.get_member(owner_id)
                if member:
                    await member.send(
                        f"📁 Seu ticket **{ticket_type.upper()}** foi fechado.\n"
                        f"Fechado por: {interaction.user.mention}\n"
                        f"Segue o transcript em TXT:",
                        file=discord.File(filepath, filename=filename)
                    )
            except Exception:
                pass

        try:
            log_file = discord.File(filepath, filename=filename)
            await log_ticket_fechado(
                guild,
                f"🔴 **TICKET FECHADO (SUPORTE)** | Tipo: **{ticket_type.upper()}** | "
                f"Dono: <@{owner_id}> | Fechado por: {interaction.user.mention} | Canal: `{channel.name}`",
                file=log_file
            )
        except Exception:
            await log_ticket_fechado(
                guild,
                f"🔴 **TICKET FECHADO (SUPORTE)** | Tipo: **{ticket_type.upper()}** | "
                f"Dono: <@{owner_id}> | Fechado por: {interaction.user.mention} | Canal: `{channel.name}`"
            )

        await channel.send("🔒 Ticket será fechado em 3 segundos…")
        await discord.utils.sleep_until(discord.utils.utcnow() + datetime.timedelta(seconds=3))
        await channel.delete(reason=f"Ticket fechado por {interaction.user} (SUPREMO)")

class PainelAjudaView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="❓ DÚVIDAS", style=discord.ButtonStyle.success, custom_id="supremo:ajuda_duvidas")
    async def duvidas(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if interaction.guild is None or not isinstance(interaction.user, discord.Member):
            return await interaction.followup.send("❌ Isso só funciona no servidor.", ephemeral=True)

        texto = (
            "🟢 **TICKET DE DÚVIDAS**\n\n"
            "**Use este ticket para:**\n"
            "• Dúvidas sobre metas, entregas, regras, cargos e pagamentos.\n\n"
            "**Envie assim:**\n"
            "1) Sua dúvida completa\n"
            "2) Print/Prova (se tiver)\n"
            "3) Seu ID (se necessário)\n\n"
            "⚠️ Não floodar."
        )
        ch = await create_help_ticket(interaction.guild, interaction.user, "duvidas", "❓ DÚVIDAS - SUPREMO", texto)
        if not ch:
            return await interaction.followup.send("❌ Categoria de suporte não configurada.", ephemeral=True)
        await interaction.followup.send(f"✅ Ticket criado: {ch.mention}", ephemeral=True)

    @discord.ui.button(label="🚨 DENÚNCIA", style=discord.ButtonStyle.danger, custom_id="supremo:ajuda_denuncia")
    async def denuncia(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if interaction.guild is None or not isinstance(interaction.user, discord.Member):
            return await interaction.followup.send("❌ Isso só funciona no servidor.", ephemeral=True)

        texto = (
            "🔴 **TICKET DE DENÚNCIA**\n\n"
            "**OBRIGATÓRIO enviar:**\n"
            "1) Nome/ID do jogador\n"
            "2) O que aconteceu\n"
            "3) Data/horário\n"
            "4) Provas: vídeo/print\n\n"
            "⚠️ Denúncia falsa = punição."
        )
        ch = await create_help_ticket(interaction.guild, interaction.user, "denuncia", "🚨 DENÚNCIA - SUPREMO", texto)
        if not ch:
            return await interaction.followup.send("❌ Categoria de suporte não configurada.", ephemeral=True)
        await interaction.followup.send(f"✅ Ticket criado: {ch.mention}", ephemeral=True)

    @discord.ui.button(label="📌 AUSÊNCIA", style=discord.ButtonStyle.primary, custom_id="supremo:ajuda_ausencia")
    async def ausencia(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if interaction.guild is None or not isinstance(interaction.user, discord.Member):
            return await interaction.followup.send("❌ Isso só funciona no servidor.", ephemeral=True)

        texto = (
            "🔵 **TICKET DE AUSÊNCIA**\n\n"
            "**Envie assim:**\n"
            "1) Motivo (se quiser)\n"
            "2) Data que vai sair\n"
            "3) Data que volta\n"
            "4) Seu cargo\n\n"
            "✅ Avisando aqui você evita perder cargo por ausência."
        )
        ch = await create_help_ticket(interaction.guild, interaction.user, "ausencia", "📌 AUSÊNCIA - SUPREMO", texto)
        if not ch:
            return await interaction.followup.send("❌ Categoria de suporte não configurada.", ephemeral=True)
        await interaction.followup.send(f"✅ Ticket criado: {ch.mention}", ephemeral=True)

# =========================================================
#  ADV (PAINEL)
# =========================================================
class ApplyAdvModal(discord.ui.Modal, title="APLICAR ADV - SUPREMO"):
    alvo = discord.ui.TextInput(label="Membro (ID ou @)", placeholder="Ex: 123456789... ou @Fulano", max_length=64)
    tipo = discord.ui.TextInput(label="Tipo (leve/moderada/grave)", placeholder="Ex: leve", max_length=16)
    prova = discord.ui.TextInput(label="Link da prova (vídeo/print)", placeholder="Cole o link aqui", max_length=200, required=False)
    motivo = discord.ui.TextInput(label="Motivo/Resumo", placeholder="Explique o motivo", style=discord.TextStyle.paragraph, max_length=700)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if interaction.guild is None or not isinstance(interaction.user, discord.Member):
            return await interaction.followup.send("❌ Use isso no servidor.", ephemeral=True)
        if not is_admin(interaction.user):
            return await interaction.followup.send("⛔ Apenas administradores.", ephemeral=True)

        guild = interaction.guild
        raw = str(self.alvo.value).strip()
        m = re.search(r"(\d{15,20})", raw)
        if not m:
            return await interaction.followup.send("❌ Envie ID correto ou mencione.", ephemeral=True)
        member = guild.get_member(int(m.group(1)))
        if not member:
            return await interaction.followup.send("❌ Membro não encontrado.", ephemeral=True)

        tipo = str(self.tipo.value).strip().lower()
        if tipo not in ("leve", "moderada", "grave"):
            return await interaction.followup.send("❌ Tipo inválido (leve/moderada/grave).", ephemeral=True)

        role_leve = guild.get_role(ADV_LEVE_ID)
        role_mod = guild.get_role(ADV_MODERADA_ID)
        role_grave = guild.get_role(ADV_GRAVE_ID)
        if not (role_leve and role_mod and role_grave):
            return await interaction.followup.send("❌ IDs de cargos ADV inválidos.", ephemeral=True)

        applied = "—"
        try:
            if tipo == "leve":
                if role_grave in member.roles:
                    applied = "ADV GRAVE (já estava)"
                elif role_mod in member.roles:
                    await member.remove_roles(role_mod, role_leve, reason="Somatória ADV -> GRAVE")
                    await member.add_roles(role_grave, reason="Somatória MOD+LEVE -> GRAVE")
                    applied = "ADV GRAVE (MOD+LEVE)"
                elif role_leve in member.roles:
                    await member.remove_roles(role_leve, reason="Somatória LEVE+LEVE -> MOD")
                    await member.add_roles(role_mod, reason="Somatória LEVE+LEVE -> MOD")
                    applied = "ADV MODERADA (LEVE+LEVE)"
                else:
                    await member.add_roles(role_leve, reason="ADV aplicada (LEVE)")
                    applied = "ADV LEVE"
            elif tipo == "moderada":
                await member.remove_roles(role_leve, role_grave, reason="Aplicando MODERADA")
                await member.add_roles(role_mod, reason="ADV aplicada (MODERADA)")
                applied = "ADV MODERADA"
            else:
                await member.remove_roles(role_leve, role_mod, reason="Aplicando GRAVE")
                await member.add_roles(role_grave, reason="ADV aplicada (GRAVE)")
                applied = "ADV GRAVE"
        except discord.Forbidden:
            return await interaction.followup.send("⚠️ Bot sem permissão para gerenciar cargos.", ephemeral=True)

        log_ch = guild.get_channel(CANAL_LOG_ADV_ID)
        prova = str(self.prova.value).strip()
        motivo = str(self.motivo.value).strip()

        if isinstance(log_ch, discord.TextChannel):
            await log_ch.send(
                f"⛔ **ADV APLICADA**\n"
                f"• Membro: {member.mention} (`{member.id}`)\n"
                f"• Resultado: **{applied}**\n"
                f"• Aplicada por: {interaction.user.mention}\n"
                f"• Prova: {prova if prova else 'Não enviada'}\n"
                f"• Motivo: {motivo}"
            )

        await interaction.followup.send(f"✅ Feito! Resultado: **{applied}** em {member.mention}", ephemeral=True)

class RemoveAdvModal(discord.ui.Modal, title="REMOVER ADV - SUPREMO"):
    alvo = discord.ui.TextInput(label="Membro (ID ou @)", placeholder="Ex: 123456789... ou @Fulano", max_length=64)
    qual = discord.ui.TextInput(label="Remover qual? (leve/moderada/grave/todas)", placeholder="Ex: todas", max_length=16)
    motivo = discord.ui.TextInput(label="Motivo/Obs", placeholder="Ex: pagamento feito", style=discord.TextStyle.paragraph, max_length=500, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if interaction.guild is None or not isinstance(interaction.user, discord.Member):
            return await interaction.followup.send("❌ Use isso no servidor.", ephemeral=True)
        if not is_admin(interaction.user):
            return await interaction.followup.send("⛔ Apenas administradores.", ephemeral=True)

        guild = interaction.guild
        raw = str(self.alvo.value).strip()
        m = re.search(r"(\d{15,20})", raw)
        if not m:
            return await interaction.followup.send("❌ Envie ID correto ou mencione.", ephemeral=True)
        member = guild.get_member(int(m.group(1)))
        if not member:
            return await interaction.followup.send("❌ Membro não encontrado.", ephemeral=True)

        qual = str(self.qual.value).strip().lower()
        if qual not in ("leve", "moderada", "grave", "todas"):
            return await interaction.followup.send("❌ Use: leve/moderada/grave/todas", ephemeral=True)

        role_leve = guild.get_role(ADV_LEVE_ID)
        role_mod = guild.get_role(ADV_MODERADA_ID)
        role_grave = guild.get_role(ADV_GRAVE_ID)

        to_remove = []
        if qual in ("leve", "todas") and role_leve:
            to_remove.append(role_leve)
        if qual in ("moderada", "todas") and role_mod:
            to_remove.append(role_mod)
        if qual in ("grave", "todas") and role_grave:
            to_remove.append(role_grave)

        try:
            if to_remove:
                await member.remove_roles(*to_remove, reason="Remoção ADV")
        except discord.Forbidden:
            return await interaction.followup.send("⚠️ Bot sem permissão para gerenciar cargos.", ephemeral=True)

        log_ch = guild.get_channel(CANAL_LOG_ADV_ID)
        obs = str(self.motivo.value).strip()

        if isinstance(log_ch, discord.TextChannel):
            await log_ch.send(
                f"✅ **ADV REMOVIDA**\n"
                f"• Membro: {member.mention} (`{member.id}`)\n"
                f"• Removido: **{qual.upper()}**\n"
                f"• Removida por: {interaction.user.mention}\n"
                f"• Obs: {obs if obs else '—'}"
            )

        await interaction.followup.send(f"✅ ADV removida (**{qual.upper()}**) de {member.mention}", ephemeral=True)

class PainelAdvView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="⛔ APLICAR ADV", style=discord.ButtonStyle.danger, custom_id="supremo:adv_apply")
    async def aplicar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_admin(interaction.user):
            return await interaction.response.send_message("⛔ Apenas administradores.", ephemeral=True)
        await interaction.response.send_modal(ApplyAdvModal())

    @discord.ui.button(label="✅ REMOVER ADV", style=discord.ButtonStyle.success, custom_id="supremo:adv_remove")
    async def remover(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_admin(interaction.user):
            return await interaction.response.send_message("⛔ Apenas administradores.", ephemeral=True)
        await interaction.response.send_modal(RemoveAdvModal())

# =========================================================
#  PEDIR TAG
# =========================================================
def role_label(guild: discord.Guild, rid: int) -> str:
    r = guild.get_role(rid)
    return r.name if r else f"ROLE {rid}"

class SolicitarCargoModal(discord.ui.Modal, title="SOLICITAR CARGO - SUPREMO"):
    cargo_id = discord.ui.TextInput(label="ID do cargo desejado (hierarquia)", placeholder="Cole o ID do cargo", max_length=32)
    motivo = discord.ui.TextInput(label="Motivo/Prova (opcional)", placeholder="Link, print, texto...", style=discord.TextStyle.paragraph, required=False, max_length=700)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if interaction.guild is None:
            return await interaction.followup.send("❌ Use isso no servidor.", ephemeral=True)

        guild = interaction.guild
        try:
            rid = int(re.sub(r"\D", "", str(self.cargo_id.value)))
        except Exception:
            return await interaction.followup.send("❌ ID inválido.", ephemeral=True)

        if rid not in HIERARQUIA_ROLE_IDS:
            return await interaction.followup.send("❌ Esse cargo não está na hierarquia.", ephemeral=True)

        channel = guild.get_channel(CANAL_PAINEL_PEDIR_TAG_ID)
        if not isinstance(channel, discord.TextChannel):
            return await interaction.followup.send("❌ Canal PEDIR TAG inválido.", ephemeral=True)

        motivo = str(self.motivo.value).strip()
        embed = discord.Embed(
            title="📌 SOLICITAÇÃO DE CARGO (HIERARQUIA)",
            description=(
                f"👤 Solicitante: {interaction.user.mention} (`{interaction.user.id}`)\n"
                f"🎯 Cargo solicitado: **{role_label(guild, rid)}** (`{rid}`)\n"
                f"📝 Motivo/Prova: {motivo if motivo else '—'}"
            ),
            color=COR_INFO
        )

        msg = await send_logo_embed_message(channel, embed)
        await channel.send(view=TagApproveView(requester_id=interaction.user.id, new_role_id=rid, source_message_id=msg.id))

        await interaction.followup.send("✅ Solicitação enviada no canal PEDIR TAG.", ephemeral=True)

class RemoverCargoModal(discord.ui.Modal, title="REMOVER / REBAIXAR CARGO - SUPREMO"):
    alvo = discord.ui.TextInput(label="Membro (ID ou @)", placeholder="Ex: 123456789... ou @Fulano", max_length=64)
    novo_cargo = discord.ui.TextInput(label="Novo cargo (ID da hierarquia) OU vazio para remover", placeholder="Cole o ID ou deixe vazio", required=False, max_length=32)
    motivo = discord.ui.TextInput(label="Motivo (opcional)", placeholder="Texto...", required=False, style=discord.TextStyle.paragraph, max_length=500)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        if interaction.guild is None or not isinstance(interaction.user, discord.Member):
            return await interaction.followup.send("❌ Use isso no servidor.", ephemeral=True)
        if not is_admin(interaction.user):
            return await interaction.followup.send("⛔ Apenas administradores.", ephemeral=True)

        guild = interaction.guild
        m = re.search(r"(\d{15,20})", str(self.alvo.value))
        if not m:
            return await interaction.followup.send("❌ Alvo inválido.", ephemeral=True)
        member = guild.get_member(int(m.group(1)))
        if not member:
            return await interaction.followup.send("❌ Membro não encontrado.", ephemeral=True)

        new_id = None
        if str(self.novo_cargo.value).strip():
            try:
                new_id = int(re.sub(r"\D", "", str(self.novo_cargo.value)))
            except Exception:
                return await interaction.followup.send("❌ Novo cargo inválido.", ephemeral=True)
            if new_id not in HIERARQUIA_ROLE_IDS:
                return await interaction.followup.send("❌ Novo cargo não está na hierarquia.", ephemeral=True)

        hier_roles = get_hierarquia_roles(guild)
        try:
            to_remove = [r for r in hier_roles if r in member.roles]
            if to_remove:
                await member.remove_roles(*to_remove, reason="Remoção/rebaixamento (admin)")
            if new_id:
                role = guild.get_role(new_id)
                if role:
                    await member.add_roles(role, reason="Rebaixamento (admin)")
        except discord.Forbidden:
            return await interaction.followup.send("⚠️ Bot sem permissão para gerenciar cargos.", ephemeral=True)

        await update_hierarquia_panel(guild)
        await interaction.followup.send("✅ Ação aplicada.", ephemeral=True)

class TagApproveView(discord.ui.View):
    def __init__(self, requester_id: int, new_role_id: int, source_message_id: int):
        super().__init__(timeout=None)
        self.requester_id = requester_id
        self.new_role_id = new_role_id
        self.source_message_id = source_message_id

    @discord.ui.button(label="✅ APROVAR", style=discord.ButtonStyle.success, custom_id="supremo:tag_aprovar")
    async def aprovar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if interaction.guild is None or not isinstance(interaction.user, discord.Member):
            return await interaction.followup.send("❌ Use no servidor.", ephemeral=True)
        if not is_admin(interaction.user):
            return await interaction.followup.send("⛔ Apenas administradores aprovam.", ephemeral=True)

        guild = interaction.guild
        member = guild.get_member(self.requester_id)
        if not member:
            return await interaction.followup.send("❌ Solicitante não encontrado.", ephemeral=True)

        try:
            await set_hierarquia_role(member, self.new_role_id, reason="Solicitação de cargo aprovada")
        except discord.Forbidden:
            return await interaction.followup.send("⚠️ Bot sem permissão para gerenciar cargos.", ephemeral=True)

        await update_hierarquia_panel(guild)

        try:
            ch = interaction.channel
            if isinstance(ch, discord.TextChannel):
                msg = await ch.fetch_message(self.source_message_id)
                emb = msg.embeds[0] if msg.embeds else discord.Embed(title="SOLICITAÇÃO")
                emb.color = COR_APROVADO_MARROM
                emb.add_field(name="✅ STATUS", value=f"Aprovado por {interaction.user.mention}", inline=False)
                await msg.edit(embed=emb, view=None)
        except Exception:
            pass

        await interaction.followup.send("✅ Aprovado e cargo atualizado (hierarquia).", ephemeral=True)

    @discord.ui.button(label="❌ REPROVAR", style=discord.ButtonStyle.danger, custom_id="supremo:tag_reprovar")
    async def reprovar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if interaction.guild is None or not isinstance(interaction.user, discord.Member):
            return await interaction.followup.send("❌ Use no servidor.", ephemeral=True)
        if not is_admin(interaction.user):
            return await interaction.followup.send("⛔ Apenas administradores reprovam.", ephemeral=True)

        try:
            ch = interaction.channel
            if isinstance(ch, discord.TextChannel):
                msg = await ch.fetch_message(self.source_message_id)
                emb = msg.embeds[0] if msg.embeds else discord.Embed(title="SOLICITAÇÃO")
                emb.color = COR_REPROVADO_VERMELHO
                emb.add_field(name="❌ STATUS", value=f"Reprovado por {interaction.user.mention}", inline=False)
                await msg.edit(embed=emb, view=None)
        except Exception:
            pass

        await interaction.followup.send("❌ Reprovado.", ephemeral=True)

class TesteEliteView(discord.ui.View):
    def __init__(self, requester_id: int):
        super().__init__(timeout=None)
        self.requester_id = requester_id

    @discord.ui.button(label="✅ APROVAR TESTE", style=discord.ButtonStyle.success, custom_id="supremo:elite_aprovar")
    async def aprovar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if interaction.guild is None or not isinstance(interaction.user, discord.Member):
            return await interaction.followup.send("❌ Use no servidor.", ephemeral=True)
        if not is_admin(interaction.user):
            return await interaction.followup.send("⛔ Apenas administradores.", ephemeral=True)

        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            return await interaction.followup.send("❌ Canal inválido.", ephemeral=True)

        guild = channel.guild
        member = guild.get_member(self.requester_id)
        if not member:
            return await interaction.followup.send("❌ Membro não encontrado.", ephemeral=True)

        try:
            await set_hierarquia_role(member, 1386444927847628840, reason="Teste Elite aprovado")  # ELITE
        except discord.Forbidden:
            return await interaction.followup.send("⚠️ Bot sem permissão para gerenciar cargos.", ephemeral=True)

        await update_hierarquia_panel(guild)

        filepath, filename = await build_text_transcript(channel)
        await log_ticket_fechado(
            guild,
            f"🔴 **TICKET FECHADO (TESTE ELITE / APROVADO)** | Autor: {member.mention} (`{member.id}`) | Aprovado por: {interaction.user.mention} | Canal: `{channel.name}`",
            file=discord.File(filepath, filename=filename)
        )

        await channel.send("✅ **TESTE ELITE APROVADO!** Ticket será fechado em 3 segundos…")
        await discord.utils.sleep_until(discord.utils.utcnow() + datetime.timedelta(seconds=3))
        await channel.delete(reason="Teste elite aprovado - fechar")

    @discord.ui.button(label="❌ REPROVAR TESTE", style=discord.ButtonStyle.danger, custom_id="supremo:elite_reprovar")
    async def reprovar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if interaction.guild is None or not isinstance(interaction.user, discord.Member):
            return await interaction.followup.send("❌ Use no servidor.", ephemeral=True)
        if not is_admin(interaction.user):
            return await interaction.followup.send("⛔ Apenas administradores.", ephemeral=True)

        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            return await interaction.followup.send("❌ Canal inválido.", ephemeral=True)

        guild = channel.guild
        member = guild.get_member(self.requester_id)

        filepath, filename = await build_text_transcript(channel)
        await log_ticket_fechado(
            guild,
            f"🔴 **TICKET FECHADO (TESTE ELITE / REPROVADO)** | Autor: {member.mention if member else self.requester_id} | Reprovado por: {interaction.user.mention} | Canal: `{channel.name}`",
            file=discord.File(filepath, filename=filename)
        )

        await channel.send("❌ **TESTE ELITE REPROVADO.** Ticket será fechado em 3 segundos…")
        await discord.utils.sleep_until(discord.utils.utcnow() + datetime.timedelta(seconds=3))
        await channel.delete(reason="Teste elite reprovado - fechar")

class PainelPedirTagView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📌 SOLICITAR CARGO", style=discord.ButtonStyle.primary, custom_id="supremo:tag_solicitar")
    async def solicitar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(SolicitarCargoModal())

    @discord.ui.button(label="🧹 REMOVER / REBAIXAR", style=discord.ButtonStyle.danger, custom_id="supremo:tag_remover")
    async def remover(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_admin(interaction.user):
            return await interaction.response.send_message("⛔ Apenas administradores.", ephemeral=True)
        await interaction.response.send_modal(RemoverCargoModal())

    @discord.ui.button(label="⚔️ FAZER TESTE ELITE", style=discord.ButtonStyle.success, custom_id="supremo:tag_teste_elite")
    async def teste_elite(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if interaction.guild is None or not isinstance(interaction.user, discord.Member):
            return await interaction.followup.send("❌ Use no servidor.", ephemeral=True)

        guild = interaction.guild
        category = guild.get_channel(CATEGORIA_TICKET_TESTE_ELITE_ID)
        if not isinstance(category, discord.CategoryChannel):
            return await interaction.followup.send("❌ Categoria do teste elite inválida.", ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        }
        for role in guild.roles:
            if role.permissions.administrator:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        ch = await guild.create_text_channel(
            name=f"teste-elite-{interaction.user.id}"[:95],
            category=category,
            overwrites=overwrites,
            reason="Ticket teste elite"
        )

        embed = discord.Embed(
            title="⚔️ TESTE ELITE - SUPREMO",
            description=(
                "✅ Use este ticket para conduzir o teste.\n\n"
                "📌 Quando finalizar, o ADMIN deve clicar em **APROVAR** ou **REPROVAR**.\n"
                "Se aprovado, o cargo de **ELITE** será aplicado automaticamente e o ticket fecha."
            ),
            color=COR_INFO
        )
        await send_logo_embed_message(ch, embed)
        await ch.send("🔧 **CONTROLE DO TESTE:**", view=TesteEliteView(requester_id=interaction.user.id))

        await log_ticket_aberto(
            guild,
            f"🟢 **TICKET ABERTO (TESTE ELITE)** | Autor: {interaction.user.mention} (`{interaction.user.id}`) | Canal: {ch.mention}"
        )

        await interaction.followup.send(f"✅ Ticket criado: {ch.mention}", ephemeral=True)

# =========================================================
#  PEDIDOS (MUAMBA corrigido)
# =========================================================
MUAMBA_PRECOS = {
    "lockpick": 30_000,
    "placa": 30_000,
    "c4": 20_000,
    "masterpick": 70_000,
    "algema": 40_000,
    "laco": 20_000,
    "laço": 20_000,
    "celular": 3_000,
    "mochila": 3_000,
    "radio": 3_000,
    "rádio": 3_000,
    "mascara": 15_000,
    "máscara": 15_000,
    "roupas": 3_000,
    "rastreador": 90_000,
    "capuz": 20_000,
    "keycard": 40_000,
}

class PedidosView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🧾 SOLICITAR PEDIDO", style=discord.ButtonStyle.success, custom_id="supremo:pedidos_abrir")
    async def abrir(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "📦 Escolha o tipo do pedido:",
            view=PedidosTipoView(),
            ephemeral=True
        )

class PedidosTipoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=120)

    @discord.ui.button(label="📦 MUAMBA", style=discord.ButtonStyle.primary)
    async def muamba(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PedidoMuambaModal())

    @discord.ui.button(label="💊 DROGAS", style=discord.ButtonStyle.primary)
    async def drogas(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PedidoDrogasModal())

    @discord.ui.button(label="🔫 MUNIÇÃO", style=discord.ButtonStyle.primary)
    async def municao(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PedidoMunicaoModal())

    @discord.ui.button(label="🧰 KIT REPARO", style=discord.ButtonStyle.primary)
    async def kit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PedidoKitModal())

class PedidoMuambaModal(discord.ui.Modal, title="PEDIDO - MUAMBA (cole os itens)"):
    itens = discord.ui.TextInput(
        label="Itens e quantidades (1 por linha)",
        placeholder="Ex:\ncelular=500\nmochila=500\nc4=10\nkeycard=20",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1200
    )
    obs = discord.ui.TextInput(
        label="OBS (troca/negócio) - opcional",
        placeholder="Se for troca, escreva aqui",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=400
    )

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            return await interaction.response.send_message("❌ Use no servidor.", ephemeral=True)

        parsed = parse_lines_item_qty(self.itens.value, normalize_names=True)
        if not parsed:
            return await interaction.response.send_message("❌ Não entendi. Use tipo: celular=500", ephemeral=True)

        total = 0
        lines = []
        unknown = []

        for name, qty in parsed:
            if name not in MUAMBA_PRECOS:
                unknown.append(name)
                continue
            price = MUAMBA_PRECOS[name]
            sub = price * qty
            total += sub
            lines.append(f"• **{name.upper()}** x{qty} = `{fmt_money_k(sub)}`")

        if not lines:
            return await interaction.response.send_message(
                "❌ Nenhum item válido.\nItens aceitos: " + ", ".join(sorted(set(MUAMBA_PRECOS.keys()))),
                ephemeral=True
            )

        obs = (self.obs.value or "").strip()
        obs_extra = f"\n⚠️ Itens ignorados (nome diferente): `{', '.join(unknown)}`" if unknown else ""

        text = (
            f"📦 **PEDIDO MUAMBA (SUPREMO)**\n"
            f"Solicitante: {interaction.user.mention}\n\n"
            + "\n".join(lines) +
            f"\n\n💰 **TOTAL:** `{fmt_money_k(total)}`\n"
            f"{('📝 OBS: ' + obs) if obs else 'OBS: se for TROCA/NEGÓCIO, descreva abaixo do pedido.'}"
            f"{obs_extra}"
        )

        canal = guild.get_channel(CANAL_PEDIDOS_ID)
        if isinstance(canal, discord.TextChannel):
            await canal.send(text)

        await interaction.response.send_message("✅ Pedido MUAMBA registrado no canal PEDIDOS.", ephemeral=True)

class PedidoDrogasModal(discord.ui.Modal, title="PEDIDO - DROGAS"):
    uso = discord.ui.TextInput(label="Drogas pra USO (2,5k cada) - qtd", required=False, max_length=6)
    venda = discord.ui.TextInput(label="Drogas pra VENDA (2,5k cada) - qtd", required=False, max_length=6)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            return await interaction.response.send_message("❌ Use no servidor.", ephemeral=True)

        price = 2_500
        q_uso = parse_int(self.uso.value)
        q_venda = parse_int(self.venda.value)

        total = (q_uso + q_venda) * price

        text = (
            f"💊 **PEDIDO DROGAS (SUPREMO)**\n"
            f"Solicitante: {interaction.user.mention}\n\n"
            f"• USO x{q_uso} = `{fmt_money_k(q_uso*price)}`\n"
            f"• VENDA x{q_venda} = `{fmt_money_k(q_venda*price)}`\n\n"
            f"💰 **TOTAL:** `{fmt_money_k(total)}`\n"
            "OBS: se for TROCA/NEGÓCIO, descreva abaixo do pedido."
        )

        canal = guild.get_channel(CANAL_PEDIDOS_ID)
        if isinstance(canal, discord.TextChannel):
            await canal.send(text)

        await interaction.response.send_message("✅ Pedido registrado no canal PEDIDOS.", ephemeral=True)

class PedidoMunicaoModal(discord.ui.Modal, title="PEDIDO - MUNIÇÃO"):
    fuzil = discord.ui.TextInput(label="Munição Fuzil (2k) - qtd", required=False, max_length=6)
    smg = discord.ui.TextInput(label="Munição SMG (1,5k) - qtd", required=False, max_length=6)
    pistola = discord.ui.TextInput(label="Munição Pistola (1k) - qtd", required=False, max_length=6)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            return await interaction.response.send_message("❌ Use no servidor.", ephemeral=True)

        prices = {"Fuzil": 2_000, "SMG": 1_500, "Pistola": 1_000}
        qf = parse_int(self.fuzil.value)
        qs = parse_int(self.smg.value)
        qp = parse_int(self.pistola.value)

        total = qf*prices["Fuzil"] + qs*prices["SMG"] + qp*prices["Pistola"]

        text = (
            f"🔫 **PEDIDO MUNIÇÃO (SUPREMO)**\n"
            f"Solicitante: {interaction.user.mention}\n\n"
            f"• Fuzil x{qf} = `{fmt_money_k(qf*prices['Fuzil'])}`\n"
            f"• SMG x{qs} = `{fmt_money_k(qs*prices['SMG'])}`\n"
            f"• Pistola x{qp} = `{fmt_money_k(qp*prices['Pistola'])}`\n\n"
            f"💰 **TOTAL:** `{fmt_money_k(total)}`\n"
            "OBS: se for TROCA/NEGÓCIO, descreva abaixo do pedido."
        )

        canal = guild.get_channel(CANAL_PEDIDOS_ID)
        if isinstance(canal, discord.TextChannel):
            await canal.send(text)

        await interaction.response.send_message("✅ Pedido registrado no canal PEDIDOS.", ephemeral=True)

class PedidoKitModal(discord.ui.Modal, title="PEDIDO - KIT REPARO"):
    norte = discord.ui.TextInput(label="Kit Norte (3k) - qtd", required=False, max_length=6)
    sul = discord.ui.TextInput(label="Kit Sul (4k) - qtd", required=False, max_length=6)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            return await interaction.response.send_message("❌ Use no servidor.", ephemeral=True)

        qn = parse_int(self.norte.value)
        qs = parse_int(self.sul.value)
        total = qn*3_000 + qs*4_000

        text = (
            f"🧰 **PEDIDO KIT REPARO (SUPREMO)**\n"
            f"Solicitante: {interaction.user.mention}\n\n"
            f"• Kit Norte x{qn} = `{fmt_money_k(qn*3000)}`\n"
            f"• Kit Sul x{qs} = `{fmt_money_k(qs*4000)}`\n\n"
            f"💰 **TOTAL:** `{fmt_money_k(total)}`\n"
            "OBS: se for TROCA/NEGÓCIO, descreva abaixo do pedido."
        )

        canal = guild.get_channel(CANAL_PEDIDOS_ID)
        if isinstance(canal, discord.TextChannel):
            await canal.send(text)

        await interaction.response.send_message("✅ Pedido registrado no canal PEDIDOS.", ephemeral=True)

# =========================================================
#  ENCOMENDAS (VÁRIAS ARMAS NO MESMO PEDIDO)
# =========================================================
WEAPONS = {
    "FIVE SEVEN (FIVE)": {"price": 180_000, "cano": 6, "mola": 10, "prata": 12, "bronze": 0, "gatilho": 4},
    "M9A3": {"price": 200_000, "cano": 6, "mola": 10, "prata": 24, "bronze": 0, "gatilho": 4},

    "SMG MK2": {"price": 270_000, "cano": 8, "mola": 16, "prata": 0, "bronze": 16, "gatilho": 6},
    "MP9": {"price": 270_000, "cano": 40, "mola": 75, "prata": 0, "bronze": 60, "gatilho": 24},
    "MTAR": {"price": 270_000, "cano": 10, "mola": 18, "prata": 0, "bronze": 20, "gatilho": 6},
    "SCORPION EVO": {"price": 290_000, "cano": 6, "mola": 14, "prata": 0, "bronze": 16, "gatilho": 8},
    "TEC-9 (TEC)": {"price": 270_000, "cano": 6, "mola": 12, "prata": 12, "bronze": 0, "gatilho": 8},

    "AK47 (AK)": {"price": 405_000, "cano": 20, "mola": 22, "prata": 24, "bronze": 0, "gatilho": 8},
    "AUG (FUZIL MILITAR)": {"price": 405_000, "cano": 20, "mola": 22, "prata": 24, "bronze": 0, "gatilho": 8},
    "NSR": {"price": 420_000, "cano": 20, "mola": 24, "prata": 24, "bronze": 0, "gatilho": 8},
    "PARAFALL": {"price": 405_000, "cano": 20, "mola": 22, "prata": 24, "bronze": 0, "gatilho": 8},
    "SCAR-H": {"price": 405_000, "cano": 20, "mola": 22, "prata": 24, "bronze": 0, "gatilho": 8},
}

WEAPON_KEY_BY_NORM = {normalize_item_name(k): k for k in WEAPONS.keys()}

def calc_brindes(pagas: int) -> int:
    if pagas <= 0:
        return 0
    if pagas >= 50:
        return (pagas // 10) * 3
    return (pagas // 10) * 2 + ((pagas % 10) // 5) * 1

class EncomendasView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🧾 REGISTRAR ENCOMENDA", style=discord.ButtonStyle.success, custom_id="supremo:encomendas_abrir")
    async def abrir(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(EncomendaModal())

class EncomendaModal(discord.ui.Modal, title="REGISTRAR ENCOMENDA (várias armas)"):
    lista = discord.ui.TextInput(
        label="Armas e quantidades (pagas) - 1 por linha",
        placeholder="Ex:\nNSR=40\nAK47 (AK)=10\nMP9=5\nTEC-9 (TEC)=20",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1200
    )
    obs = discord.ui.TextInput(
        label="OBS (opcional)",
        placeholder="Troca/negócio/obs...",
        required=False,
        style=discord.TextStyle.paragraph,
        max_length=500
    )

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            return await interaction.response.send_message("❌ Use no servidor.", ephemeral=True)

        parsed_raw = parse_lines_item_qty(self.lista.value, normalize_names=False)
        if not parsed_raw:
            return await interaction.response.send_message("❌ Formato inválido. Ex: NSR=40", ephemeral=True)

        total_preco = 0
        total_fabricar = 0
        total_brindes = 0

        mats = {"cano": 0, "mola": 0, "prata": 0, "bronze": 0, "gatilho": 0}
        partes_sup = 0
        partes_inf = 0

        linhas_resumo = []
        desconhecidas = []

        for raw_name, qty_pagas in parsed_raw:
            if qty_pagas <= 0:
                continue

            key_norm = normalize_item_name(raw_name)
            weapon_key = WEAPON_KEY_BY_NORM.get(key_norm)
            if not weapon_key:
                desconhecidas.append(raw_name.strip())
                continue

            w = WEAPONS[weapon_key]
            brindes = calc_brindes(qty_pagas)
            fabricar = qty_pagas + brindes

            total_preco += w["price"] * qty_pagas
            total_fabricar += fabricar
            total_brindes += brindes

            mats["cano"] += w["cano"] * fabricar
            mats["mola"] += w["mola"] * fabricar
            mats["prata"] += w["prata"] * fabricar
            mats["bronze"] += w["bronze"] * fabricar
            mats["gatilho"] += w["gatilho"] * fabricar

            partes_sup += fabricar * 2
            partes_inf += fabricar * 2

            linhas_resumo.append(
                f"• `{weapon_key}` | pagas: `{qty_pagas}` | brindes: `{brindes}` | fabricar: `{fabricar}` | total: `{fmt_money_k(w['price']*qty_pagas)}`"
            )

        if not linhas_resumo:
            lista_validas = "\n".join([f"• {k}" for k in WEAPONS.keys()])
            return await interaction.response.send_message(
                "❌ Nenhuma arma válida.\nUse exatamente uma da lista:\n" + lista_validas,
                ephemeral=True
            )

        obs = (self.obs.value or "").strip()
        extra = f"\n⚠️ Armas ignoradas (nome diferente): `{', '.join(desconhecidas)}`" if desconhecidas else ""

        text = (
            f"🔫 **ENCOMENDA SUPREMO (MÚLTIPLAS ARMAS)**\n"
            f"Solicitante: {interaction.user.mention}\n\n"
            f"**RESUMO:**\n" + "\n".join(linhas_resumo) +
            f"\n\n🎁 **BRINDES (total):** `{total_brindes}`\n"
            f"📦 **TOTAL A FABRICAR (pagas+brindes):** `{total_fabricar}`\n\n"
            f"🧩 **PARTES (total):**\n"
            f"• Parte Superior: `{partes_sup}`\n"
            f"• Parte Inferior: `{partes_inf}`\n\n"
            f"🧰 **MATERIAIS (total):**\n"
            f"• Cano: `{mats['cano']}`\n"
            f"• Mola: `{mats['mola']}`\n"
            f"• Prata: `{mats['prata']}`\n"
            f"• Bronze: `{mats['bronze']}`\n"
            f"• Gatilho: `{mats['gatilho']}`\n\n"
            f"💰 **TOTAL (somente pagas):** `{fmt_money_k(total_preco)}`\n"
            f"{('📝 OBS: ' + obs) if obs else ''}"
            f"{extra}"
        ).strip()

        canal = guild.get_channel(CANAL_ENCOMENDAS_ID)
        if isinstance(canal, discord.TextChannel):
            await canal.send(text)

        await interaction.response.send_message("✅ Encomenda registrada no canal ENCOMENDAS.", ephemeral=True)

# =========================================================
#  !setmeuticket
# =========================================================
@bot.command(name="setmeuticket")
@commands.guild_only()
async def setmeuticket(ctx: commands.Context):
    MEU_TICKET_MAP[str(ctx.author.id)] = ctx.channel.id
    save_json(SET_TICKET_FILE, MEU_TICKET_MAP)
    await ctx.reply("✅ Fechado! A partir de agora, quando você aprovar recrutamento, vou registrar aqui também.")

# =========================================================
#  SLASH COMMANDS (PAINÉIS)
# =========================================================
@bot.tree.command(name="painel", description="Postar painel de recrutamento (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def painel(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    embed = discord.Embed(
        title="📋 PAINEL DE RECRUTAMENTO - SUPREMO",
        description="Clique no botão abaixo para iniciar seu recrutamento.\n\n⚠️ Preencha corretamente todas as informações.",
        color=COR_PENDENTE
    )
    await send_logo_embed_message(interaction.channel, embed)
    await interaction.channel.send(view=StartRecruitView())

    await interaction.followup.send("✅ Painel de recrutamento enviado.", ephemeral=True)

@bot.tree.command(name="painel_hierarquia", description="Criar/Atualizar painel AO VIVO da hierarquia (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def painel_hierarquia(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if interaction.guild is None:
        return await interaction.followup.send("❌ Use no servidor.", ephemeral=True)

    await ensure_hierarquia_panel(interaction.guild)
    await update_hierarquia_panel(interaction.guild)

    await interaction.followup.send("✅ Painel de hierarquia atualizado no canal.", ephemeral=True)

@bot.tree.command(name="painel_ajuda", description="Postar painel de Tickets & Ajuda (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def painel_ajuda(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    if interaction.guild is None:
        return await interaction.followup.send("❌ Local inválido.", ephemeral=True)

    target = interaction.guild.get_channel(CANAL_PAINEL_AJUDA_ID)
    if not isinstance(target, discord.TextChannel):
        return await interaction.followup.send("❌ CANAL_PAINEL_AJUDA_ID inválido.", ephemeral=True)

    embed = discord.Embed(
        title="📢📌 TICKET E AJUDA",
        description="Escolha um botão para abrir ticket: **Dúvidas**, **Denúncia** ou **Ausência**.",
        color=COR_PENDENTE
    )
    await send_logo_embed_message(target, embed)
    await target.send(view=PainelAjudaView())

    await interaction.followup.send("✅ Painel de Tickets & Ajuda enviado.", ephemeral=True)

@bot.tree.command(name="painel_adv", description="Postar painel APLICA ADV (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def painel_adv(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if interaction.guild is None:
        return await interaction.followup.send("❌ Local inválido.", ephemeral=True)

    target = interaction.guild.get_channel(CANAL_PAINEL_ADV_ID)
    if not isinstance(target, discord.TextChannel):
        return await interaction.followup.send("❌ CANAL_PAINEL_ADV_ID inválido.", ephemeral=True)

    texto = (
        "⚠️ **CANAL CRIADO PARA CONCEDER AS ADV's** ⚠️\n\n"
        "⛔ **ADV LEVE** (chamar atenção)\n"
        "⛔ **ADV MODERADA** (perde cargo 1/2 semana dependendo)\n"
        "⛔❗ **ADV GRAVE** (PD da fac)\n\n"
        "📌 **SOMATÓRIA:**\n"
        "• LEVE + LEVE = MODERADA\n"
        "• MODERADA + LEVE = GRAVE\n"
        "• GRAVE = EXO (manual)\n\n"
        "💰 **REMOVER ADV (pagamento):**\n"
        "• 1x LEVE = 1.5kk\n"
        "• 1x MODERADA = 2.5kk\n"
        "• GRAVE não remove\n\n"
        "🏦 PIX: `supremos`"
    )
    embed = discord.Embed(title="⚠️ APLICA ADV - SUPREMO", description=texto, color=COR_REPROVADO_VERMELHO)
    await send_logo_embed_message(target, embed)
    await target.send(view=PainelAdvView())

    await interaction.followup.send("✅ Painel ADV enviado.", ephemeral=True)

@bot.tree.command(name="painel_tag", description="Postar painel PEDIR TAG (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def painel_tag(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if interaction.guild is None:
        return await interaction.followup.send("❌ Local inválido.", ephemeral=True)

    target = interaction.guild.get_channel(CANAL_PAINEL_PEDIR_TAG_ID)
    if not isinstance(target, discord.TextChannel):
        return await interaction.followup.send("❌ CANAL_PAINEL_PEDIR_TAG_ID inválido.", ephemeral=True)

    guild = interaction.guild
    roles_list = []
    for rid in HIERARQUIA_ROLE_IDS_ORDERED:
        roles_list.append(f"• {role_label(guild, rid)} = `{rid}`")
    roles_text = "\n".join(roles_list)

    embed = discord.Embed(
        title="🏷️ PEDIR TAG / HIERARQUIA - SUPREMO",
        description=(
            "📌 Use este painel para:\n"
            "1) **Solicitar cargo** (qualquer cargo da hierarquia)\n"
            "2) **Remover/Rebaixar** (somente ADMIN)\n"
            "3) **Fazer teste Elite** (abre ticket)\n\n"
            "⚠️ **Somente ADMIN aprova** solicitações.\n\n"
            "**Cargos (ordem padrão Supremo):**\n"
            f"{roles_text}"
        ),
        color=COR_INFO
    )
    await send_logo_embed_message(target, embed)
    await target.send(view=PainelPedirTagView())

    await interaction.followup.send("✅ Painel PEDIR TAG enviado.", ephemeral=True)

@bot.tree.command(name="painel_pedidos", description="Postar painel de PEDIDOS (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def painel_pedidos(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if interaction.guild is None:
        return await interaction.followup.send("❌ Use no servidor.", ephemeral=True)

    canal = interaction.guild.get_channel(CANAL_PEDIDOS_ID)
    if not isinstance(canal, discord.TextChannel):
        return await interaction.followup.send("❌ CANAL_PEDIDOS_ID inválido.", ephemeral=True)

    embed = discord.Embed(
        title="📦 PEDIDOS SUPREMO",
        description=(
            "Clique em **SOLICITAR PEDIDO** e preencha as quantidades.\n"
            "O bot calcula tudo automaticamente e registra aqui no canal."
        ),
        color=COR_INFO
    )
    await send_logo_embed_message(canal, embed)
    await canal.send("✅ **PAINEL DE PEDIDOS**", view=PedidosView())
    await interaction.followup.send("✅ Painel de PEDIDOS enviado.", ephemeral=True)

@bot.tree.command(name="painel_encomendas", description="Postar painel de ENCOMENDAS (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def painel_encomendas(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    if interaction.guild is None:
        return await interaction.followup.send("❌ Use no servidor.", ephemeral=True)

    canal = interaction.guild.get_channel(CANAL_ENCOMENDAS_ID)
    if not isinstance(canal, discord.TextChannel):
        return await interaction.followup.send("❌ CANAL_ENCOMENDAS_ID inválido.", ephemeral=True)

    embed = discord.Embed(
        title="🔫 ENCOMENDAS SUPREMO",
        description=(
            "Clique em **REGISTRAR ENCOMENDA**.\n"
            "Cole várias armas (1 por linha) e o bot calcula brindes, peças, partes e total."
        ),
        color=COR_INFO
    )
    await send_logo_embed_message(canal, embed)
    await canal.send("✅ **PAINEL DE ENCOMENDAS**", view=EncomendasView())
    await interaction.followup.send("✅ Painel de ENCOMENDAS enviado.", ephemeral=True)

# =========================================================
#  EVENTS
# =========================================================
@bot.event
async def on_ready():
    bot.add_view(StartRecruitView())
    bot.add_view(ApproveView())
    bot.add_view(PainelAjudaView())
    bot.add_view(TicketControlView())
    bot.add_view(PainelAdvView())
    bot.add_view(PainelPedirTagView())
    bot.add_view(PedidosView())
    bot.add_view(EncomendasView())

    try:
        await bot.tree.sync()
    except Exception as e:
        print(f"[SYNC] Erro ao sincronizar slash commands: {e}")

    print(f"🔥 BOT SUPREMO ONLINE: {bot.user} ({bot.user.id})")

@bot.event
async def on_member_join(member: discord.Member):
    # sem cargo ao entrar
    try:
        embed = discord.Embed(
            title="📋 RECRUTAMENTO - SUPREMO",
            description="Clique no botão abaixo para preencher o recrutamento e abrir seu ticket.",
            color=COR_PENDENTE
        )
        await send_logo_embed_message(member, embed)
        await member.send(view=StartRecruitView())
    except discord.Forbidden:
        pass
    except Exception:
        pass

# =========================================================
#  RUN
# =========================================================
if not TOKEN:
    raise RuntimeError("❌ DISCORD_TOKEN não encontrado no .env")

bot.run(TOKEN)

