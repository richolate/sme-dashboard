import { relations } from "drizzle-orm/relations";
import { djangoContentType, authPermission, authGroup, authGroupPermissions, users, usersGroups, usersUserPermissions, djangoAdminLog, uploadHistory } from "./schema";

export const authPermissionRelations = relations(authPermission, ({one, many}) => ({
	djangoContentType: one(djangoContentType, {
		fields: [authPermission.contentTypeId],
		references: [djangoContentType.id]
	}),
	authGroupPermissions: many(authGroupPermissions),
	usersUserPermissions: many(usersUserPermissions),
}));

export const djangoContentTypeRelations = relations(djangoContentType, ({many}) => ({
	authPermissions: many(authPermission),
	djangoAdminLogs: many(djangoAdminLog),
}));

export const authGroupPermissionsRelations = relations(authGroupPermissions, ({one}) => ({
	authGroup: one(authGroup, {
		fields: [authGroupPermissions.groupId],
		references: [authGroup.id]
	}),
	authPermission: one(authPermission, {
		fields: [authGroupPermissions.permissionId],
		references: [authPermission.id]
	}),
}));

export const authGroupRelations = relations(authGroup, ({many}) => ({
	authGroupPermissions: many(authGroupPermissions),
	usersGroups: many(usersGroups),
}));

export const usersGroupsRelations = relations(usersGroups, ({one}) => ({
	user: one(users, {
		fields: [usersGroups.userId],
		references: [users.id]
	}),
	authGroup: one(authGroup, {
		fields: [usersGroups.groupId],
		references: [authGroup.id]
	}),
}));

export const usersRelations = relations(users, ({many}) => ({
	usersGroups: many(usersGroups),
	usersUserPermissions: many(usersUserPermissions),
	djangoAdminLogs: many(djangoAdminLog),
	uploadHistories: many(uploadHistory),
}));

export const usersUserPermissionsRelations = relations(usersUserPermissions, ({one}) => ({
	user: one(users, {
		fields: [usersUserPermissions.userId],
		references: [users.id]
	}),
	authPermission: one(authPermission, {
		fields: [usersUserPermissions.permissionId],
		references: [authPermission.id]
	}),
}));

export const djangoAdminLogRelations = relations(djangoAdminLog, ({one}) => ({
	djangoContentType: one(djangoContentType, {
		fields: [djangoAdminLog.contentTypeId],
		references: [djangoContentType.id]
	}),
	user: one(users, {
		fields: [djangoAdminLog.userId],
		references: [users.id]
	}),
}));

export const uploadHistoryRelations = relations(uploadHistory, ({one}) => ({
	user: one(users, {
		fields: [uploadHistory.uploadedById],
		references: [users.id]
	}),
}));