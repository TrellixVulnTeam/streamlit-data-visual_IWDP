import pandas as pd
import streamlit as st
import altair as alt
import json

# Title
st.set_page_config(layout="wide")
st.title("Statistik Produksi Minyak Mentah")

# Import JSON
f = open("kode_negara_lengkap.json")
object = json.load(f)
f.close()

# Dictionary pembantu
kode2name = {}
name2kode = {}
for item in object:
    kode2name[item['alpha-3']] = item['name']
    name2kode[item['name']] = item['alpha-3']

# Load dataset
df = pd.read_csv("produksi_minyak_mentah.csv")

# 1. Grafik jumlah produksi minyak terhadap waktu suatu negara N
st.subheader("Grafik Tahunan Produksi Minyak Negara")
negara_selected = st.selectbox("Pilih negara", name2kode.keys())

a_selected = df.loc[df['kode_negara'] ==
                    name2kode[negara_selected]]  # Filter sesuai kode
if(len(a_selected) == 0):
    st.markdown("Jumlah produksi tidak diketahui")
else:
    st.altair_chart(alt.Chart(a_selected).mark_line().encode(
        x=alt.X('tahun:N', axis=alt.Axis(title='Tahun')),
        y=alt.Y('produksi', axis=alt.Axis(title='Produksi'))
    ).properties(title=f'''Grafik Produksi Minyak Tahunan Negara {negara_selected}'''), use_container_width=True)

# 2. Grafik B negara penghasil terbesar pada tahun T
st.subheader("Grafik Top Negara Penghasil Terbesar")
tahun_selected = st.slider(
    'Pilih tahun', min_value=1971, max_value=2015, value=1971)
b_selected = df.loc[df['tahun'] == tahun_selected]  # Filter sesuai tahun

b_selected['name'] = b_selected['kode_negara'].map(
    kode2name)  # tambahkan kolom name
# Drop kolom yang tidak punya nama seperti G20 dkk
b_selected = b_selected.loc[b_selected['name'].notna()]
b_selected = b_selected.drop(columns=['kode_negara', 'tahun'], axis=1).sort_values(
    by='produksi', ascending=False)

if(len(b_selected) == 0):
    st.markdown("Jumlah produksi tidak diketahui")
else:
    banyak_negara_selected = st.slider(
        'Pilih berapa banyak negara', min_value=1, max_value=len(b_selected), value=1)
    st.altair_chart(alt.Chart(b_selected[:banyak_negara_selected]).mark_bar().encode(
        x=alt.X('name', sort=None, axis=alt.Axis(title='Negara')),
        y=alt.Y('produksi', axis=alt.Axis(title='Produksi'))
    ).properties(title=f'''Grafik Top {banyak_negara_selected} pada Tahun {tahun_selected}''', height=600), use_container_width=True)

# 3. Grafik B negara total kumulatif
st.subheader("Grafik top negara total kumulatif")

c_selected = df.drop(columns=['tahun'], axis=1)
c_selected = c_selected.groupby(['kode_negara']).sum().sort_values(
    by='produksi', ascending=False).reset_index()
c_selected['name'] = c_selected['kode_negara'].map(kode2name)
c_selected = c_selected.loc[c_selected['name'].notna()]

banyak_negara_selected = st.slider(
    'Pilih berapa banyak negara', min_value=1, max_value=len(c_selected), value=1)
st.altair_chart(alt.Chart(c_selected[:banyak_negara_selected]).mark_bar().encode(
    x=alt.X('name', sort=None, axis=alt.Axis(title='Negara')),
    y=alt.Y('produksi', axis=alt.Axis(title='Produksi'))
).properties(title=f'''Grafik Top {banyak_negara_selected} Kumulatif''', height=600), use_container_width=True)

# 4. Informasi produksi
left, right = st.columns(2)

# 4a
left.subheader("Informasi Produksi Terbesar")
big_cumul_name = c_selected.iloc[0]['name']  # Kumulatif bisa pakai nomor 3
big_cumul_code = ''
big_cumul_region = ''
big_cumul_subreg = ''
big_cumul_produksi = c_selected.iloc[0]['produksi']

big_tahun_selected = left.slider(
    'Pilih tahun', min_value=1971, max_value=2015, value=1971, key=1)
big = df.loc[df['tahun'] == big_tahun_selected]  # Filter sesuai tahun
big = big.sort_values(by='produksi', ascending=False)

big['name'] = big['kode_negara'].map(kode2name)
big = big.loc[big['name'].notna()]

big_name = big.iloc[0]['name']
big_code = ''
big_region = ''
big_subreg = ''
big_produksi = big.iloc[0]['produksi']

for item in object:
    if item['name'] == big_cumul_name:
        big_cumul_code = item['country-code']
        big_cumul_region = item['region']
        big_cumul_subreg = item['sub-region']

    if item['name'] == big_name:
        big_code = item['country-code']
        big_region = item['region']
        big_subreg = item['sub-region']

# Buat dataframe agar bisa ditampilkan sebagai tabel
big = pd.DataFrame({'Condition': [str(big_tahun_selected), 'Kumulatif'], 'Nama Lengkap': [big_name, big_cumul_name], 'Kode Negara': [big_code, big_cumul_code], 'Region': [
    big_region, big_cumul_region], 'Sub-region': [big_subreg, big_cumul_subreg], 'Produksi': [big_produksi, big_cumul_produksi]}).set_index('Condition')

left.table(big)


# 4b
right.subheader("Informasi Produksi Terkecil")

# Perlu agar nol tidak terdeteksi minimum
nonzero = c_selected.loc[c_selected['produksi'] != 0]
small_cumul_name = nonzero.iloc[-1]['name']
small_cumul_code = ''
small_cumul_region = ''
small_cumul_subreg = ''
small_cumul_produksi = nonzero.iloc[-1]['produksi']

small_tahun_selected = right.slider(
    'Pilih tahun', min_value=1971, max_value=2015, value=1971, key=2)
small = df.loc[df['tahun'] == small_tahun_selected]
small = small.loc[small['produksi'] != 0]
small = small.sort_values(by='produksi', ascending=False)

small['name'] = small['kode_negara'].map(kode2name)
small = small.loc[small['name'].notna()]

small_name = small.iloc[-1]['name']
small_code = ''
small_region = ''
small_subreg = ''
small_produksi = small.iloc[-1]['produksi']

for item in object:
    if item['name'] == small_cumul_name:
        small_cumul_code = item['country-code']
        small_cumul_region = item['region']
        small_cumul_subreg = item['sub-region']

    if item['name'] == small_name:
        small_code = item['country-code']
        small_region = item['region']
        small_subreg = item['sub-region']

small = pd.DataFrame({'Condition': [str(small_tahun_selected), 'Kumulatif'], 'Nama Lengkap': [small_name, small_cumul_name], 'Kode Negara': [small_code, small_cumul_code], 'Region': [
    small_region, small_cumul_region], 'Sub-region': [small_subreg, small_cumul_subreg], 'Produksi': [small_produksi, small_cumul_produksi]}).set_index('Condition')

right.table(small)

# 4c
left.subheader("Informasi Produksi Nol")

zero_tahun_selected = left.slider(
    'Pilih tahun', min_value=1971, max_value=2015, value=1971, key=3)
zero = df.loc[df['tahun'] == zero_tahun_selected]
zero = zero.loc[zero['produksi'] == 0]
zero['name'] = zero['kode_negara'].map(kode2name)
zero = zero.loc[zero['name'].notna()]

zero_name = zero['name']
zero_code = []
zero_region = []
zero_subreg = []
zero_produksi = zero['produksi']

for name in zero_name:
    for item in object:
        if name == item['name']:
            zero_code.append(item['country-code'])
            zero_region.append(item['region'])
            zero_subreg.append(item['sub-region'])

zero = pd.DataFrame({'Nama Lengkap': zero_name, 'Kode Negara': zero_code, 'Region': zero_region,
                    'Sub-region': zero_subreg, 'Produksi': zero_produksi}).reset_index(drop=True)
left.markdown(f"Banyak negara {len(zero)}")
left.table(zero)

right.subheader(" ")
right.subheader(" ")
right.subheader(" ")
right.subheader(" ")
right.subheader(" ")

right.markdown("Kumulatif")

newzero = c_selected.loc[c_selected['produksi'] == 0]

zero_cumul_name = newzero['name']
zero_cumul_code = []
zero_cumul_region = []
zero_cumul_subreg = []
zero_cumul_produksi = newzero['produksi']

for name in zero_cumul_name:
    for item in object:
        if name == item['name']:
            zero_cumul_code.append(item['country-code'])
            zero_cumul_region.append(item['region'])
            zero_cumul_subreg.append(item['sub-region'])

zero_cumul = pd.DataFrame({'Nama Lengkap': zero_cumul_name, 'Kode Negara': zero_cumul_code, 'Region': zero_cumul_region,
                          'Sub-region': zero_cumul_subreg, 'Produksi': zero_cumul_produksi}).reset_index(drop=True)

right.subheader(" ")
right.subheader(" ")
right.markdown(f"Banyak negara {len(zero_cumul)}")
right.table(zero_cumul)
