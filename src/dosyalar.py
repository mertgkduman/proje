"""Kaynaklı parti dosyalarının ortak doğrulama işlemleri."""


def foundation_for_party(db, party_id):
    """Partinin sicille doğrulanmış kuruluş tarihini döndür."""
    # Gecikmeli import: arşiv yazıcısı bu modülü de kullanır.
    from arsiv import check_identity

    identities = db.execute(
        "SELECT * FROM identity_observation WHERE entity_id=? AND entity_kind='party' AND valid_from IS NOT NULL",
        (party_id,),
    ).fetchall()
    if len(identities) != 1:
        raise ValueError('Parti için tek doğrulanmış kuruluş tarihi gerekli')
    identity = dict(identities[0])
    check_identity(db, identity)
    return identity['valid_from']
