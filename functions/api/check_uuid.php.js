const AVATAR_FILE = "69ad879cb2271_6861408193_1772980124.jpg";
const SIGNATURE_FILE = "69ad87c37f602_6861408193_1772980163.png";

export async function onRequestGet() {
  const payload = {
    code: "ok",
    version: "cf-pages",
    doc_number: "011408193",
    rnocpp_number: "3933519353",
    fio: "Ісматов Андрій Валерович",
    translit: "Ismatov Andrii Valerovych",
    get_organ: "8193",
    sex: "Ч",
    edocument: 1,
    login_code: "0",
    qr_enable: 0,
    qr_disable_text: "CF PAGES",
    offline_mode: 0,
    cords: "м. КИЇВ\nM. KYIV",
    birth_street: 0,
    birth_street_date: 0,
    passport_start: "07.10.2025",
    passport_end: "07.10.2035",
    number_unzr: "11092007-39180",
    img: AVATAR_FILE.replace(/\.[^.]+$/, ""),
    signature: SIGNATURE_FILE.replace(/\.[^.]+$/, ""),
    date: "11.09.2007",
    watermark: 1,
    renew: new Date().toLocaleString("uk-UA"),
    barcode: Date.now(),
    is_ban: 0,
    ban_reason: "",
    international: 0,
    international_start: "23.09.2023",
    international_end: "23.09.2033",
    international_number: "GP093166",
    avatarUrl: `/api/avatars/${AVATAR_FILE}`,
    signatureUrl: `/api/signature/${SIGNATURE_FILE}`,
  };

  return new Response(JSON.stringify(payload), {
    status: 200,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store",
      "Access-Control-Allow-Origin": "*",
    },
  });
}

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET,POST,PUT,PATCH,DELETE,OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    },
  });
}
