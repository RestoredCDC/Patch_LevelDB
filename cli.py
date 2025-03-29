# cli.py

import argparse
from patchlib import initialize_db, apply_patch_action, list_patches, export_audit_html

def main():
    parser = argparse.ArgumentParser(
        description="RestoredCDC Patch Tool"
    )

    subparsers = parser.add_subparsers(
        dest="command", required=True
    )

    common_args = [
        ("--db", {"required": True, "help": "Path to patch LevelDB"}),
        ("--key", {"required": True, "help": "Key to patch"}),
        ("--reason", {"required": True, "help": "Reason for the patch"})
    ]

    apply_parser = subparsers.add_parser(
        "apply-text", help="Apply a text/HTML patch"
    )
    for arg, opts in common_args:
        apply_parser.add_argument(arg, **opts)
    apply_parser.add_argument("--file", required=True)
    apply_parser.add_argument("--mimetype", default=None)

    binary_parser = subparsers.add_parser(
        "add-binary", help="Add a binary (image, PDF) patch"
    )
    
    for arg, opts in common_args:
        binary_parser.add_argument(arg, **opts)
    binary_parser.add_argument("--file", required=True)
    binary_parser.add_argument("--mimetype", required=True)

    subparsers.add_parser("list-patches", help="List audit log")

    remove_parser = subparsers.add_parser(
        "remove-patch", help="Remove patch by key"
    )
    
    for arg, opts in common_args:
        remove_parser.add_argument(arg, **opts)

    export_parser = subparsers.add_parser(
        "export-audit-html", help="Export audit log as HTML"
    )
    export_parser.add_argument("--output", required=True)

    args = parser.parse_args()

    if args.command == "list-patches":
        list_patches()
    elif args.command == "export-audit-html":
        export_audit_html(args.output)
    else:
        patch_db, patch_content_db, patch_mimetype_db = initialize_db(args.db)

        if args.command == "remove-patch":
            apply_patch_action(
                patch_content_db, patch_mimetype_db, args.key,
                action="remove", reason=args.reason
            )
        elif args.command == "apply-text":
            apply_patch_action(
                patch_content_db, patch_mimetype_db, args.key,
                action="add", reason=args.reason,
                data=args.file, mimetype=args.mimetype,
                mode="text"
            )
        elif args.command == "add-binary":
            apply_patch_action(
                patch_content_db, patch_mimetype_db, args.key,
                action="add", reason=args.reason,
                filepath=args.file, mimetype=args.mimetype,
                mode="binary"
            )
        patch_db.close()

if __name__ == "__main__":
    main()
