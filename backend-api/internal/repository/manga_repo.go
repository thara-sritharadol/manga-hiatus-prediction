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
			"title_th", "title_jp", "title_en", "vol_th", "vol_raw", 
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

// GenerateMLFeatures, manga_ml_features
func (r *MangaRepository) GenerateMLFeatures() error {

	if err := r.DB.Exec("TRUNCATE TABLE manga_ml_features").Error; err != nil {
		return err
	}

	query := `
		INSERT INTO manga_ml_features (
			title_th, title_en, latest_release_date, max_vol_th, jp_total_vols, 
			total_premium_issues, jikan_status, days_since_release, volume_gap, is_dropped, updated_at
		)
		SELECT 
			title_th,
			MAX(title_en),
			MAX(th_release_date),
			MAX(vol_th),
			MAX(jp_total_vols),
			SUM(has_premium),
			MAX(jikan_status),
			
			CURRENT_DATE - DATE(MAX(th_release_date)),
			
			GREATEST(0, MAX(jp_total_vols) - MAX(vol_th)),
			
			CASE 
				WHEN MAX(jikan_status) IN ('HIATUS', 'CANCELLED') THEN 0
				WHEN (CURRENT_DATE - DATE(MAX(th_release_date))) > 730 
					 AND GREATEST(0, MAX(jp_total_vols) - MAX(vol_th)) >= 3 THEN 1
				ELSE 0
			END,
			
			CURRENT_TIMESTAMP -- updated_at
		FROM phoenix_mangas
		WHERE media_type = 'Manga'
		GROUP BY title_th;
	`
	
	result := r.DB.Exec(query)
	return result.Error
}