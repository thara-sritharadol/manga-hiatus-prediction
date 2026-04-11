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
			"has_premium", "premium_type", "th_release_date", "updated_at",
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