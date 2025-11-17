import { pgTable, bigint, varchar, timestamp, unique, integer, index, foreignKey, boolean, check, text, smallint, date, jsonb, numeric } from "drizzle-orm/pg-core"
import { sql } from "drizzle-orm"



export const djangoMigrations = pgTable("django_migrations", {
	// You can use { mode: "bigint" } if numbers are exceeding js number limitations
	id: bigint({ mode: "number" }).primaryKey().generatedByDefaultAsIdentity({ name: "django_migrations_id_seq", startWith: 1, increment: 1, minValue: 1, maxValue: 9223372036854775807, cache: 1 }),
	app: varchar({ length: 255 }).notNull(),
	name: varchar({ length: 255 }).notNull(),
	applied: timestamp({ withTimezone: true, mode: 'string' }).notNull(),
});

export const djangoContentType = pgTable("django_content_type", {
	id: integer().primaryKey().generatedByDefaultAsIdentity({ name: "django_content_type_id_seq", startWith: 1, increment: 1, minValue: 1, maxValue: 2147483647, cache: 1 }),
	appLabel: varchar("app_label", { length: 100 }).notNull(),
	model: varchar({ length: 100 }).notNull(),
}, (table) => [
	unique("django_content_type_app_label_model_76bd3d3b_uniq").on(table.appLabel, table.model),
]);

export const authPermission = pgTable("auth_permission", {
	id: integer().primaryKey().generatedByDefaultAsIdentity({ name: "auth_permission_id_seq", startWith: 1, increment: 1, minValue: 1, maxValue: 2147483647, cache: 1 }),
	name: varchar({ length: 255 }).notNull(),
	contentTypeId: integer("content_type_id").notNull(),
	codename: varchar({ length: 100 }).notNull(),
}, (table) => [
	index("auth_permission_content_type_id_2f476e4b").using("btree", table.contentTypeId.asc().nullsLast().op("int4_ops")),
	foreignKey({
			columns: [table.contentTypeId],
			foreignColumns: [djangoContentType.id],
			name: "auth_permission_content_type_id_2f476e4b_fk_django_co"
		}),
	unique("auth_permission_content_type_id_codename_01ab375a_uniq").on(table.contentTypeId, table.codename),
]);

export const authGroup = pgTable("auth_group", {
	id: integer().primaryKey().generatedByDefaultAsIdentity({ name: "auth_group_id_seq", startWith: 1, increment: 1, minValue: 1, maxValue: 2147483647, cache: 1 }),
	name: varchar({ length: 150 }).notNull(),
}, (table) => [
	index("auth_group_name_a6ea08ec_like").using("btree", table.name.asc().nullsLast().op("varchar_pattern_ops")),
	unique("auth_group_name_key").on(table.name),
]);

export const authGroupPermissions = pgTable("auth_group_permissions", {
	// You can use { mode: "bigint" } if numbers are exceeding js number limitations
	id: bigint({ mode: "number" }).primaryKey().generatedByDefaultAsIdentity({ name: "auth_group_permissions_id_seq", startWith: 1, increment: 1, minValue: 1, maxValue: 9223372036854775807, cache: 1 }),
	groupId: integer("group_id").notNull(),
	permissionId: integer("permission_id").notNull(),
}, (table) => [
	index("auth_group_permissions_group_id_b120cbf9").using("btree", table.groupId.asc().nullsLast().op("int4_ops")),
	index("auth_group_permissions_permission_id_84c5c92e").using("btree", table.permissionId.asc().nullsLast().op("int4_ops")),
	foreignKey({
			columns: [table.groupId],
			foreignColumns: [authGroup.id],
			name: "auth_group_permissions_group_id_b120cbf9_fk_auth_group_id"
		}),
	foreignKey({
			columns: [table.permissionId],
			foreignColumns: [authPermission.id],
			name: "auth_group_permissio_permission_id_84c5c92e_fk_auth_perm"
		}),
	unique("auth_group_permissions_group_id_permission_id_0cd325b0_uniq").on(table.groupId, table.permissionId),
]);

export const users = pgTable("users", {
	// You can use { mode: "bigint" } if numbers are exceeding js number limitations
	id: bigint({ mode: "number" }).primaryKey().generatedByDefaultAsIdentity({ name: "users_id_seq", startWith: 1, increment: 1, minValue: 1, maxValue: 9223372036854775807, cache: 1 }),
	password: varchar({ length: 128 }).notNull(),
	lastLogin: timestamp("last_login", { withTimezone: true, mode: 'string' }),
	isSuperuser: boolean("is_superuser").notNull(),
	username: varchar({ length: 150 }).notNull(),
	firstName: varchar("first_name", { length: 150 }).notNull(),
	lastName: varchar("last_name", { length: 150 }).notNull(),
	email: varchar({ length: 254 }).notNull(),
	isStaff: boolean("is_staff").notNull(),
	isActive: boolean("is_active").notNull(),
	dateJoined: timestamp("date_joined", { withTimezone: true, mode: 'string' }).notNull(),
	role: varchar({ length: 10 }).notNull(),
	phoneNumber: varchar("phone_number", { length: 15 }),
	createdAt: timestamp("created_at", { withTimezone: true, mode: 'string' }).notNull(),
	updatedAt: timestamp("updated_at", { withTimezone: true, mode: 'string' }).notNull(),
}, (table) => [
	index("users_username_e8658fc8_like").using("btree", table.username.asc().nullsLast().op("varchar_pattern_ops")),
	unique("users_username_key").on(table.username),
]);

export const usersGroups = pgTable("users_groups", {
	// You can use { mode: "bigint" } if numbers are exceeding js number limitations
	id: bigint({ mode: "number" }).primaryKey().generatedByDefaultAsIdentity({ name: "users_groups_id_seq", startWith: 1, increment: 1, minValue: 1, maxValue: 9223372036854775807, cache: 1 }),
	// You can use { mode: "bigint" } if numbers are exceeding js number limitations
	userId: bigint("user_id", { mode: "number" }).notNull(),
	groupId: integer("group_id").notNull(),
}, (table) => [
	index("users_groups_group_id_2f3517aa").using("btree", table.groupId.asc().nullsLast().op("int4_ops")),
	index("users_groups_user_id_f500bee5").using("btree", table.userId.asc().nullsLast().op("int8_ops")),
	foreignKey({
			columns: [table.userId],
			foreignColumns: [users.id],
			name: "users_groups_user_id_f500bee5_fk_users_id"
		}),
	foreignKey({
			columns: [table.groupId],
			foreignColumns: [authGroup.id],
			name: "users_groups_group_id_2f3517aa_fk_auth_group_id"
		}),
	unique("users_groups_user_id_group_id_fc7788e8_uniq").on(table.userId, table.groupId),
]);

export const usersUserPermissions = pgTable("users_user_permissions", {
	// You can use { mode: "bigint" } if numbers are exceeding js number limitations
	id: bigint({ mode: "number" }).primaryKey().generatedByDefaultAsIdentity({ name: "users_user_permissions_id_seq", startWith: 1, increment: 1, minValue: 1, maxValue: 9223372036854775807, cache: 1 }),
	// You can use { mode: "bigint" } if numbers are exceeding js number limitations
	userId: bigint("user_id", { mode: "number" }).notNull(),
	permissionId: integer("permission_id").notNull(),
}, (table) => [
	index("users_user_permissions_permission_id_6d08dcd2").using("btree", table.permissionId.asc().nullsLast().op("int4_ops")),
	index("users_user_permissions_user_id_92473840").using("btree", table.userId.asc().nullsLast().op("int8_ops")),
	foreignKey({
			columns: [table.userId],
			foreignColumns: [users.id],
			name: "users_user_permissions_user_id_92473840_fk_users_id"
		}),
	foreignKey({
			columns: [table.permissionId],
			foreignColumns: [authPermission.id],
			name: "users_user_permissio_permission_id_6d08dcd2_fk_auth_perm"
		}),
	unique("users_user_permissions_user_id_permission_id_3b86cbdf_uniq").on(table.userId, table.permissionId),
]);

export const djangoAdminLog = pgTable("django_admin_log", {
	id: integer().primaryKey().generatedByDefaultAsIdentity({ name: "django_admin_log_id_seq", startWith: 1, increment: 1, minValue: 1, maxValue: 2147483647, cache: 1 }),
	actionTime: timestamp("action_time", { withTimezone: true, mode: 'string' }).notNull(),
	objectId: text("object_id"),
	objectRepr: varchar("object_repr", { length: 200 }).notNull(),
	actionFlag: smallint("action_flag").notNull(),
	changeMessage: text("change_message").notNull(),
	contentTypeId: integer("content_type_id"),
	// You can use { mode: "bigint" } if numbers are exceeding js number limitations
	userId: bigint("user_id", { mode: "number" }).notNull(),
}, (table) => [
	index("django_admin_log_content_type_id_c4bce8eb").using("btree", table.contentTypeId.asc().nullsLast().op("int4_ops")),
	index("django_admin_log_user_id_c564eba6").using("btree", table.userId.asc().nullsLast().op("int8_ops")),
	foreignKey({
			columns: [table.contentTypeId],
			foreignColumns: [djangoContentType.id],
			name: "django_admin_log_content_type_id_c4bce8eb_fk_django_co"
		}),
	foreignKey({
			columns: [table.userId],
			foreignColumns: [users.id],
			name: "django_admin_log_user_id_c564eba6_fk_users_id"
		}),
	check("django_admin_log_action_flag_check", sql`action_flag >= 0`),
]);

export const processedData = pgTable("processed_data", {
	// You can use { mode: "bigint" } if numbers are exceeding js number limitations
	id: bigint({ mode: "number" }).primaryKey().generatedByDefaultAsIdentity({ name: "processed_data_id_seq", startWith: 1, increment: 1, minValue: 1, maxValue: 9223372036854775807, cache: 1 }),
	dataType: varchar("data_type", { length: 50 }).notNull(),
	subType: varchar("sub_type", { length: 50 }).notNull(),
	date: date().notNull(),
	processedJson: jsonb("processed_json").notNull(),
	createdAt: timestamp("created_at", { withTimezone: true, mode: 'string' }).notNull(),
	updatedAt: timestamp("updated_at", { withTimezone: true, mode: 'string' }).notNull(),
}, (table) => [
	index("processed_data_data_type_927b7fb2").using("btree", table.dataType.asc().nullsLast().op("text_ops")),
	index("processed_data_data_type_927b7fb2_like").using("btree", table.dataType.asc().nullsLast().op("varchar_pattern_ops")),
	index("processed_data_date_7817b3a1").using("btree", table.date.asc().nullsLast().op("date_ops")),
	unique("processed_data_data_type_sub_type_date_3961c8e2_uniq").on(table.dataType, table.subType, table.date),
]);

export const lw321 = pgTable("lw321", {
	// You can use { mode: "bigint" } if numbers are exceeding js number limitations
	id: bigint({ mode: "number" }).primaryKey().generatedByDefaultAsIdentity({ name: "loan_data_id_seq", startWith: 1, increment: 1, minValue: 1, maxValue: 9223372036854775807, cache: 1 }),
	periode: varchar({ length: 30 }).notNull(),
	kanca: varchar({ length: 150 }).notNull(),
	kodeUker: varchar("kode_uker", { length: 50 }).notNull(),
	uker: varchar({ length: 150 }).notNull(),
	lnType: varchar("ln_type", { length: 50 }).notNull(),
	nomorRekening: varchar("nomor_rekening", { length: 50 }).notNull(),
	namaDebitur: varchar("nama_debitur", { length: 200 }).notNull(),
	plafon: numeric({ precision: 18, scale:  2 }),
	nextPmtDate: date("next_pmt_date"),
	nextIntPmtDate: date("next_int_pmt_date"),
	rate: numeric({ precision: 7, scale:  4 }),
	tglMenunggak: date("tgl_menunggak"),
	tglRealisasi: date("tgl_realisasi"),
	tglJatuhTempo: date("tgl_jatuh_tempo"),
	jangkaWaktu: integer("jangka_waktu"),
	flagRestruk: varchar("flag_restruk", { length: 50 }).notNull(),
	cifNo: varchar("cif_no", { length: 50 }).notNull(),
	kolektibilitasLancar: varchar("kolektibilitas_lancar", { length: 50 }).notNull(),
	kolektibilitasDpk: varchar("kolektibilitas_dpk", { length: 50 }).notNull(),
	kolektibilitasKurangLancar: varchar("kolektibilitas_kurang_lancar", { length: 50 }).notNull(),
	kolektibilitasDiragukan: varchar("kolektibilitas_diragukan", { length: 50 }).notNull(),
	kolektibilitasMacet: varchar("kolektibilitas_macet", { length: 50 }).notNull(),
	tunggakanPokok: numeric("tunggakan_pokok", { precision: 18, scale:  2 }),
	tunggakanBunga: numeric("tunggakan_bunga", { precision: 18, scale:  2 }),
	tunggakanPinalti: numeric("tunggakan_pinalti", { precision: 18, scale:  2 }),
	code: varchar({ length: 50 }).notNull(),
	description: varchar({ length: 255 }).notNull(),
	kolAdk: varchar("kol_adk", { length: 50 }).notNull(),
	pnPengelolaSinglepn: varchar("pn_pengelola_singlepn", { length: 150 }).notNull(),
	pnPengelola1: varchar("pn_pengelola_1", { length: 150 }).notNull(),
	pnPemrakarsa: varchar("pn_pemrakarsa", { length: 150 }).notNull(),
	pnReferral: varchar("pn_referral", { length: 150 }).notNull(),
	pnRestruk: varchar("pn_restruk", { length: 150 }).notNull(),
	pnPengelola2: varchar("pn_pengelola_2", { length: 150 }).notNull(),
	pnPemutus: varchar("pn_pemutus", { length: 150 }).notNull(),
	pnCrm: varchar("pn_crm", { length: 150 }).notNull(),
	pnRmReferralNaikSegmentasi: varchar("pn_rm_referral_naik_segmentasi", { length: 150 }).notNull(),
	pnRmCrr: varchar("pn_rm_crr", { length: 150 }).notNull(),
	createdAt: timestamp("created_at", { withTimezone: true, mode: 'string' }).notNull(),
	updatedAt: timestamp("updated_at", { withTimezone: true, mode: 'string' }).notNull(),
}, (table) => [
	index("loan_data_nomor_r_aaa7d0_idx").using("btree", table.nomorRekening.asc().nullsLast().op("text_ops")),
	index("loan_data_nomor_rekening_40f18396_like").using("btree", table.nomorRekening.asc().nullsLast().op("varchar_pattern_ops")),
	index("loan_data_periode_6df3a4_idx").using("btree", table.periode.asc().nullsLast().op("text_ops"), table.kolektibilitasMacet.asc().nullsLast().op("text_ops")),
	index("loan_data_periode_7e1f2d71").using("btree", table.periode.asc().nullsLast().op("text_ops")),
	index("loan_data_periode_7e1f2d71_like").using("btree", table.periode.asc().nullsLast().op("varchar_pattern_ops")),
	index("loan_data_periode_db8448_idx").using("btree", table.periode.asc().nullsLast().op("text_ops"), table.kanca.asc().nullsLast().op("text_ops")),
	unique("loan_data_nomor_rekening_key").on(table.nomorRekening),
]);

export const uploadHistory = pgTable("upload_history", {
	// You can use { mode: "bigint" } if numbers are exceeding js number limitations
	id: bigint({ mode: "number" }).primaryKey().generatedByDefaultAsIdentity({ name: "upload_history_id_seq", startWith: 1, increment: 1, minValue: 1, maxValue: 9223372036854775807, cache: 1 }),
	fileName: varchar("file_name", { length: 255 }).notNull(),
	filePath: varchar("file_path", { length: 100 }).notNull(),
	// You can use { mode: "bigint" } if numbers are exceeding js number limitations
	fileSize: bigint("file_size", { mode: "number" }).notNull(),
	totalRows: integer("total_rows").notNull(),
	successfulRows: integer("successful_rows").notNull(),
	failedRows: integer("failed_rows").notNull(),
	status: varchar({ length: 20 }).notNull(),
	errorLog: text("error_log"),
	notes: text(),
	createdAt: timestamp("created_at", { withTimezone: true, mode: 'string' }).notNull(),
	completedAt: timestamp("completed_at", { withTimezone: true, mode: 'string' }),
	// You can use { mode: "bigint" } if numbers are exceeding js number limitations
	uploadedById: bigint("uploaded_by_id", { mode: "number" }).notNull(),
}, (table) => [
	index("upload_history_uploaded_by_id_d40cb3a9").using("btree", table.uploadedById.asc().nullsLast().op("int8_ops")),
	foreignKey({
			columns: [table.uploadedById],
			foreignColumns: [users.id],
			name: "upload_history_uploaded_by_id_d40cb3a9_fk_users_id"
		}),
]);

export const djangoSession = pgTable("django_session", {
	sessionKey: varchar("session_key", { length: 40 }).primaryKey().notNull(),
	sessionData: text("session_data").notNull(),
	expireDate: timestamp("expire_date", { withTimezone: true, mode: 'string' }).notNull(),
}, (table) => [
	index("django_session_expire_date_a5c62663").using("btree", table.expireDate.asc().nullsLast().op("timestamptz_ops")),
	index("django_session_session_key_c0390e0f_like").using("btree", table.sessionKey.asc().nullsLast().op("varchar_pattern_ops")),
]);
