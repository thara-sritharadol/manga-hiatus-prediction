package repository

import (
	"backend-api/internal/domain"

	"gorm.io/gorm"
	"gorm.io/gorm/clause"
)

type MangaRepository struct {
	DB *gorm.DB
}

// ฟังก์ชันสร้าง Repo ใหม่ (คล้าย Constructor)
func NewMangaRepository(db *gorm.DB) *MangaRepository {
	return &MangaRepository{DB: db}
}

// UPSERT
func (r *MangaRepository) Upsert(manga *domain.PhoenixManga) error {
	result := r.DB.Clauses(clause.OnConflict{
		Columns: []clause.Column{{Name: "url"}},
		DoUpdates: clause.AssignmentColumns([]string{
			"title_th", "title_en", "vol_th", "vol_raw", 
			"has_premium", "premium_type", "media_type","price",
			"authors", "genres", 
			"th_release_date", "updated_at",
			"jp_total_vols", "jikan_status",
			
		}),
	}).Create(manga)

	return result.Error
}

func (r *MangaRepository) GetPendingByStatus(status string) ([]domain.PhoenixManga, error) {
	var mangas []domain.PhoenixManga

	result := r.DB.Where("title_en != ? AND title_en != ? AND jikan_status = ?", "", "ไม่พบข้อมูลภาษาอังกฤษ", status).Find(&mangas)
	
	return mangas, result.Error
}

// ImputeEnglishTitles ทำหน้าที่ซ่อมแซมชื่อภาษาอังกฤษที่ขาดหายไป
func (r *MangaRepository) ImputeEnglishTitles() (int64, error) {
	query := `
		UPDATE phoenix_mangas AS t1
		SET title_en = t2.title_en
		FROM phoenix_mangas AS t2
		WHERE t1.title_th = t2.title_th
		  AND t1.title_en IN ('ไม่พบข้อมูลภาษาอังกฤษ', 'ไม่พบวงเล็บ', '')
		  AND t2.title_en NOT IN ('ไม่พบข้อมูลภาษาอังกฤษ', 'ไม่พบวงเล็บ', '')
	`
	
	// ใช้ Exec ของ GORM เพื่อรัน Raw SQL
	result := r.DB.Exec(query)
	
	// ส่งกลับจำนวนแถวที่ถูกอัปเดต และ Error (ถ้ามี)
	return result.RowsAffected, result.Error
}